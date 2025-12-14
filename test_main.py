#!/usr/bin/env python3

import unittest
from unittest.mock import Mock, patch, MagicMock
import tornado.testing
import tornado.web
import redis.exceptions

import main


class TestMainHandler(tornado.testing.AsyncHTTPTestCase):
    def get_app(self):
        return main.make_app(autoreload=False, debug=False, serve_traceback=False)

    def test_get(self):
        response = self.fetch('/')
        self.assertEqual(response.code, 200)


class TestHospitalHandler(tornado.testing.AsyncHTTPTestCase):
    def get_app(self):
        return main.make_app(autoreload=False, debug=False, serve_traceback=False)

    @patch('main.r')
    def test_get_success(self, mock_redis):
        """Test successful GET request for hospitals"""
        mock_redis.get.return_value = b'2'
        mock_redis.hgetall.side_effect = [
            {b'name': b'Hospital 1', b'address': b'Address 1', b'phone': b'123456', b'beds_number': b'100'},
            {b'name': b'Hospital 2', b'address': b'Address 2', b'phone': b'789012', b'beds_number': b'200'}
        ]
        
        response = self.fetch('/hospital')
        self.assertEqual(response.code, 200)

    @patch('main.r')
    def test_get_empty(self, mock_redis):
        """Test GET request when no hospitals exist"""
        mock_redis.get.return_value = b'0'
        
        response = self.fetch('/hospital')
        self.assertEqual(response.code, 200)

    @patch('main.r')
    def test_get_redis_connection_error(self, mock_redis):
        """Test GET request when Redis connection fails"""
        mock_redis.get.side_effect = redis.exceptions.ConnectionError()
        
        response = self.fetch('/hospital')
        self.assertEqual(response.code, 400)
        self.assertIn(b'Redis connection refused', response.body)

    @patch('main.r')
    def test_post_success(self, mock_redis):
        """Test successful POST request to create hospital"""
        mock_redis.get.return_value = b'1'
        mock_redis.hset.return_value = 1
        
        response = self.fetch('/hospital', method='POST', body='name=Test Hospital&address=Test Address&beds_number=100&phone=123456')
        self.assertEqual(response.code, 200)
        self.assertIn(b'OK: ID 1 for Test Hospital', response.body)
        self.assertEqual(mock_redis.hset.call_count, 4)
        mock_redis.incr.assert_called_once_with("hospital:autoID")

    @patch('main.r')
    def test_post_missing_name(self, mock_redis):
        """Test POST request with missing name"""
        response = self.fetch('/hospital', method='POST', body='address=Test Address&beds_number=100&phone=123456')
        self.assertEqual(response.code, 400)
        self.assertIn(b'Hospital name and address required', response.body)

    @patch('main.r')
    def test_post_missing_address(self, mock_redis):
        """Test POST request with missing address"""
        response = self.fetch('/hospital', method='POST', body='name=Test Hospital&beds_number=100&phone=123456')
        self.assertEqual(response.code, 400)
        self.assertIn(b'Hospital name and address required', response.body)

    @patch('main.r')
    def test_post_redis_connection_error(self, mock_redis):
        """Test POST request when Redis connection fails"""
        mock_redis.get.side_effect = redis.exceptions.ConnectionError()
        
        response = self.fetch('/hospital', method='POST', body='name=Test Hospital&address=Test Address&beds_number=100&phone=123456')
        self.assertEqual(response.code, 400)
        self.assertIn(b'Redis connection refused', response.body)

    @patch('main.r')
    def test_post_hset_failure(self, mock_redis):
        """Test POST request when hset fails"""
        mock_redis.get.return_value = b'1'
        mock_redis.hset.return_value = 0  # Simulate failure
        
        response = self.fetch('/hospital', method='POST', body='name=Test Hospital&address=Test Address&beds_number=100&phone=123456')
        self.assertEqual(response.code, 500)
        self.assertIn(b'Something went terribly wrong', response.body)


class TestDoctorHandler(tornado.testing.AsyncHTTPTestCase):
    def get_app(self):
        return main.make_app(autoreload=False, debug=False, serve_traceback=False)

    @patch('main.r')
    def test_get_success(self, mock_redis):
        """Test successful GET request for doctors"""
        mock_redis.get.return_value = b'2'
        mock_redis.hgetall.side_effect = [
            {b'surname': b'Doctor 1', b'profession': b'Surgeon', b'hospital_ID': b'0'},
            {b'surname': b'Doctor 2', b'profession': b'Physician', b'hospital_ID': b'1'}
        ]
        
        response = self.fetch('/doctor')
        self.assertEqual(response.code, 200)

    @patch('main.r')
    def test_get_redis_connection_error(self, mock_redis):
        """Test GET request when Redis connection fails"""
        mock_redis.get.side_effect = redis.exceptions.ConnectionError()
        
        response = self.fetch('/doctor')
        self.assertEqual(response.code, 400)
        self.assertIn(b'Redis connection refused', response.body)

    @patch('main.r')
    def test_post_success(self, mock_redis):
        """Test successful POST request to create doctor"""
        mock_redis.get.return_value = b'1'
        mock_redis.hset.return_value = 1
        
        response = self.fetch('/doctor', method='POST', body='surname=Smith&profession=Surgeon&hospital_ID=0')
        self.assertEqual(response.code, 200)
        self.assertIn(b'OK: ID 1 for Smith', response.body)
        self.assertEqual(mock_redis.hset.call_count, 3)
        mock_redis.incr.assert_called_once_with("doctor:autoID")

    @patch('main.r')
    def test_post_with_valid_hospital(self, mock_redis):
        """Test POST request with valid hospital ID"""
        mock_redis.get.return_value = b'1'
        mock_redis.hgetall.return_value = {b'name': b'Hospital 1'}
        mock_redis.hset.return_value = 1
        
        response = self.fetch('/doctor', method='POST', body='surname=Smith&profession=Surgeon&hospital_ID=0')
        self.assertEqual(response.code, 200)

    @patch('main.r')
    def test_post_with_invalid_hospital(self, mock_redis):
        """Test POST request with invalid hospital ID"""
        mock_redis.get.return_value = b'1'
        mock_redis.hgetall.return_value = {}  # Hospital doesn't exist
        
        response = self.fetch('/doctor', method='POST', body='surname=Smith&profession=Surgeon&hospital_ID=999')
        self.assertEqual(response.code, 400)
        self.assertIn(b'No hospital with such ID', response.body)

    @patch('main.r')
    def test_post_missing_surname(self, mock_redis):
        """Test POST request with missing surname"""
        response = self.fetch('/doctor', method='POST', body='profession=Surgeon&hospital_ID=0')
        self.assertEqual(response.code, 400)
        self.assertIn(b'Surname and profession required', response.body)

    @patch('main.r')
    def test_post_missing_profession(self, mock_redis):
        """Test POST request with missing profession"""
        response = self.fetch('/doctor', method='POST', body='surname=Smith&hospital_ID=0')
        self.assertEqual(response.code, 400)
        self.assertIn(b'Surname and profession required', response.body)

    @patch('main.r')
    def test_post_redis_connection_error(self, mock_redis):
        """Test POST request when Redis connection fails"""
        mock_redis.get.side_effect = redis.exceptions.ConnectionError()
        
        response = self.fetch('/doctor', method='POST', body='surname=Smith&profession=Surgeon&hospital_ID=0')
        self.assertEqual(response.code, 400)
        self.assertIn(b'Redis connection refused', response.body)

    @patch('main.r')
    def test_post_hset_failure(self, mock_redis):
        """Test POST request when hset fails"""
        mock_redis.get.return_value = b'1'
        mock_redis.hset.return_value = 0  # Simulate failure
        
        response = self.fetch('/doctor', method='POST', body='surname=Smith&profession=Surgeon&hospital_ID=0')
        self.assertEqual(response.code, 500)
        self.assertIn(b'Something went terribly wrong', response.body)


class TestPatientHandler(tornado.testing.AsyncHTTPTestCase):
    def get_app(self):
        return main.make_app(autoreload=False, debug=False, serve_traceback=False)

    @patch('main.r')
    def test_get_success(self, mock_redis):
        """Test successful GET request for patients"""
        mock_redis.get.return_value = b'2'
        mock_redis.hgetall.side_effect = [
            {b'surname': b'Patient 1', b'born_date': b'1990-01-01', b'sex': b'M', b'mpn': b'123456'},
            {b'surname': b'Patient 2', b'born_date': b'1991-01-01', b'sex': b'F', b'mpn': b'789012'}
        ]
        
        response = self.fetch('/patient')
        self.assertEqual(response.code, 200)

    @patch('main.r')
    def test_get_redis_connection_error(self, mock_redis):
        """Test GET request when Redis connection fails"""
        mock_redis.get.side_effect = redis.exceptions.ConnectionError()
        
        response = self.fetch('/patient')
        self.assertEqual(response.code, 400)
        self.assertIn(b'Redis connection refused', response.body)

    @patch('main.r')
    def test_post_success(self, mock_redis):
        """Test successful POST request to create patient"""
        mock_redis.get.return_value = b'1'
        mock_redis.hset.return_value = 1
        
        response = self.fetch('/patient', method='POST', body='surname=Doe&born_date=1990-01-01&sex=M&mpn=123456')
        self.assertEqual(response.code, 200)
        self.assertIn(b'OK: ID 1 for Doe', response.body)
        self.assertEqual(mock_redis.hset.call_count, 4)
        mock_redis.incr.assert_called_once_with("patient:autoID")

    @patch('main.r')
    def test_post_missing_fields(self, mock_redis):
        """Test POST request with missing required fields"""
        response = self.fetch('/patient', method='POST', body='surname=Doe&born_date=1990-01-01')
        self.assertEqual(response.code, 400)
        self.assertIn(b'All fields required', response.body)

    @patch('main.r')
    def test_post_invalid_sex(self, mock_redis):
        """Test POST request with invalid sex value"""
        response = self.fetch('/patient', method='POST', body='surname=Doe&born_date=1990-01-01&sex=X&mpn=123456')
        self.assertEqual(response.code, 400)
        self.assertIn(b'Sex must be \'M\' or \'F\'', response.body)

    @patch('main.r')
    def test_post_valid_sex_female(self, mock_redis):
        """Test POST request with valid sex value F"""
        mock_redis.get.return_value = b'1'
        mock_redis.hset.return_value = 1
        
        response = self.fetch('/patient', method='POST', body='surname=Doe&born_date=1990-01-01&sex=F&mpn=123456')
        self.assertEqual(response.code, 200)

    @patch('main.r')
    def test_post_redis_connection_error(self, mock_redis):
        """Test POST request when Redis connection fails"""
        mock_redis.get.side_effect = redis.exceptions.ConnectionError()
        
        response = self.fetch('/patient', method='POST', body='surname=Doe&born_date=1990-01-01&sex=M&mpn=123456')
        self.assertEqual(response.code, 400)
        self.assertIn(b'Redis connection refused', response.body)

    @patch('main.r')
    def test_post_hset_failure(self, mock_redis):
        """Test POST request when hset fails"""
        mock_redis.get.return_value = b'1'
        mock_redis.hset.return_value = 0  # Simulate failure
        
        response = self.fetch('/patient', method='POST', body='surname=Doe&born_date=1990-01-01&sex=M&mpn=123456')
        self.assertEqual(response.code, 500)
        self.assertIn(b'Something went terribly wrong', response.body)


class TestDiagnosisHandler(tornado.testing.AsyncHTTPTestCase):
    def get_app(self):
        return main.make_app(autoreload=False, debug=False, serve_traceback=False)

    @patch('main.r')
    def test_get_success(self, mock_redis):
        """Test successful GET request for diagnoses"""
        mock_redis.get.return_value = b'2'
        mock_redis.hgetall.side_effect = [
            {b'patient_ID': b'0', b'type': b'Flu', b'information': b'Patient has flu'},
            {b'patient_ID': b'1', b'type': b'Cold', b'information': b'Patient has cold'}
        ]
        
        response = self.fetch('/diagnosis')
        self.assertEqual(response.code, 200)

    @patch('main.r')
    def test_get_redis_connection_error(self, mock_redis):
        """Test GET request when Redis connection fails"""
        mock_redis.get.side_effect = redis.exceptions.ConnectionError()
        
        response = self.fetch('/diagnosis')
        self.assertEqual(response.code, 400)
        self.assertIn(b'Redis connection refused', response.body)

    @patch('main.r')
    def test_post_success(self, mock_redis):
        """Test successful POST request to create diagnosis"""
        mock_redis.get.return_value = b'1'
        mock_redis.hgetall.return_value = {b'surname': b'Doe'}
        mock_redis.hset.return_value = 1
        
        response = self.fetch('/diagnosis', method='POST', body='patient_ID=0&type=Flu&information=Patient has flu')
        self.assertEqual(response.code, 200)
        self.assertIn(b'OK: ID 1 for patient Doe', response.body)
        self.assertEqual(mock_redis.hset.call_count, 3)
        mock_redis.incr.assert_called_once_with("diagnosis:autoID")

    @patch('main.r')
    def test_post_missing_patient_id(self, mock_redis):
        """Test POST request with missing patient ID"""
        response = self.fetch('/diagnosis', method='POST', body='type=Flu&information=Patient has flu')
        self.assertEqual(response.code, 400)
        self.assertIn(b'Patiend ID and diagnosis type required', response.body)

    @patch('main.r')
    def test_post_missing_type(self, mock_redis):
        """Test POST request with missing diagnosis type"""
        response = self.fetch('/diagnosis', method='POST', body='patient_ID=0&information=Patient has flu')
        self.assertEqual(response.code, 400)
        self.assertIn(b'Patiend ID and diagnosis type required', response.body)

    @patch('main.r')
    def test_post_invalid_patient_id(self, mock_redis):
        """Test POST request with invalid patient ID"""
        mock_redis.get.return_value = b'1'
        mock_redis.hgetall.return_value = {}  # Patient doesn't exist
        
        response = self.fetch('/diagnosis', method='POST', body='patient_ID=999&type=Flu&information=Patient has flu')
        self.assertEqual(response.code, 400)
        self.assertIn(b'No patient with such ID', response.body)

    @patch('main.r')
    def test_post_redis_connection_error(self, mock_redis):
        """Test POST request when Redis connection fails"""
        mock_redis.get.side_effect = redis.exceptions.ConnectionError()
        
        response = self.fetch('/diagnosis', method='POST', body='patient_ID=0&type=Flu&information=Patient has flu')
        self.assertEqual(response.code, 400)
        self.assertIn(b'Redis connection refused', response.body)

    @patch('main.r')
    def test_post_hset_failure(self, mock_redis):
        """Test POST request when hset fails"""
        mock_redis.get.return_value = b'1'
        mock_redis.hgetall.return_value = {b'surname': b'Doe'}
        mock_redis.hset.return_value = 0  # Simulate failure
        
        response = self.fetch('/diagnosis', method='POST', body='patient_ID=0&type=Flu&information=Patient has flu')
        self.assertEqual(response.code, 500)
        self.assertIn(b'Something went terribly wrong', response.body)


class TestDoctorPatientHandler(tornado.testing.AsyncHTTPTestCase):
    def get_app(self):
        return main.make_app(autoreload=False, debug=False, serve_traceback=False)

    @patch('main.r')
    def test_get_success(self, mock_redis):
        """Test successful GET request for doctor-patient relationships"""
        mock_redis.get.return_value = b'2'
        mock_redis.smembers.side_effect = [
            {b'0', b'1'},
            set()
        ]
        
        response = self.fetch('/doctor-patient')
        self.assertEqual(response.code, 200)

    @patch('main.r')
    def test_get_redis_connection_error(self, mock_redis):
        """Test GET request when Redis connection fails"""
        mock_redis.get.side_effect = redis.exceptions.ConnectionError()
        
        response = self.fetch('/doctor-patient')
        self.assertEqual(response.code, 400)
        self.assertIn(b'Redis connection refused', response.body)

    @patch('main.r')
    def test_post_success(self, mock_redis):
        """Test successful POST request to create doctor-patient relationship"""
        mock_redis.hgetall.side_effect = [
            {b'surname': b'Doe'},  # patient
            {b'surname': b'Smith'}  # doctor
        ]
        mock_redis.sadd.return_value = 1
        
        response = self.fetch('/doctor-patient', method='POST', body='doctor_ID=0&patient_ID=1')
        self.assertEqual(response.code, 200)
        self.assertIn(b'OK: doctor ID: 0, patient ID: 1', response.body)
        mock_redis.sadd.assert_called_once_with("doctor-patient:0", "1")

    @patch('main.r')
    def test_post_missing_doctor_id(self, mock_redis):
        """Test POST request with missing doctor ID"""
        response = self.fetch('/doctor-patient', method='POST', body='patient_ID=1')
        self.assertEqual(response.code, 400)
        self.assertIn(b'ID required', response.body)

    @patch('main.r')
    def test_post_missing_patient_id(self, mock_redis):
        """Test POST request with missing patient ID"""
        response = self.fetch('/doctor-patient', method='POST', body='doctor_ID=0')
        self.assertEqual(response.code, 400)
        self.assertIn(b'ID required', response.body)

    @patch('main.r')
    def test_post_invalid_doctor_id(self, mock_redis):
        """Test POST request with invalid doctor ID"""
        mock_redis.hgetall.side_effect = [
            {b'surname': b'Doe'},  # patient exists
            {}  # doctor doesn't exist
        ]
        
        response = self.fetch('/doctor-patient', method='POST', body='doctor_ID=999&patient_ID=0')
        self.assertEqual(response.code, 400)
        self.assertIn(b'No such ID for doctor or patient', response.body)

    @patch('main.r')
    def test_post_invalid_patient_id(self, mock_redis):
        """Test POST request with invalid patient ID"""
        mock_redis.hgetall.side_effect = [
            {},  # patient doesn't exist
            {b'surname': b'Smith'}  # doctor exists
        ]
        
        response = self.fetch('/doctor-patient', method='POST', body='doctor_ID=0&patient_ID=999')
        self.assertEqual(response.code, 400)
        self.assertIn(b'No such ID for doctor or patient', response.body)

    @patch('main.r')
    def test_post_redis_connection_error(self, mock_redis):
        """Test POST request when Redis connection fails"""
        mock_redis.hgetall.side_effect = redis.exceptions.ConnectionError()
        
        response = self.fetch('/doctor-patient', method='POST', body='doctor_ID=0&patient_ID=1')
        self.assertEqual(response.code, 400)
        self.assertIn(b'Redis connection refused', response.body)


class TestInitDB(unittest.TestCase):
    @patch('main.r')
    def test_init_db_first_time(self, mock_redis):
        """Test init_db when database is not initialized"""
        mock_redis.get.return_value = None
        
        main.init_db()
        
        self.assertEqual(mock_redis.set.call_count, 5)
        mock_redis.set.assert_any_call("hospital:autoID", 1)
        mock_redis.set.assert_any_call("doctor:autoID", 1)
        mock_redis.set.assert_any_call("patient:autoID", 1)
        mock_redis.set.assert_any_call("diagnosis:autoID", 1)
        mock_redis.set.assert_any_call("db_initiated", 1)

    @patch('main.r')
    def test_init_db_already_initialized(self, mock_redis):
        """Test init_db when database is already initialized"""
        mock_redis.get.return_value = b'1'
        
        main.init_db()
        
        mock_redis.set.assert_not_called()


class TestAnalyticsHandler(tornado.testing.AsyncHTTPTestCase):
    def get_app(self):
        return main.make_app(autoreload=False, debug=False, serve_traceback=False)

    @patch('main.r')
    def test_get_analytics_success(self, mock_redis):
        """Test successful GET request for analytics"""
        # Use a function to return appropriate values based on key
        def get_side_effect(key):
            key_str = key.decode() if isinstance(key, bytes) else str(key)
            if key_str == 'hospital:autoID':
                return b'2'
            elif key_str == 'doctor:autoID':
                return b'3'
            elif key_str == 'patient:autoID':
                return b'4'
            elif key_str == 'diagnosis:autoID':
                return b'2'
            elif key_str == 'db_initiated':
                return b'1'
            return None
        
        def hgetall_side_effect(key):
            key_str = key.decode() if isinstance(key, bytes) else str(key)
            if key_str == 'hospital:0':
                return {b'name': b'Hospital 1', b'beds_number': b'100'}
            elif key_str == 'hospital:1':
                return {b'name': b'Hospital 2', b'beds_number': b'200'}
            elif key_str == 'doctor:0':
                return {b'surname': b'Doctor 1', b'hospital_ID': b'0'}
            elif key_str == 'doctor:1':
                return {b'surname': b'Doctor 2', b'hospital_ID': b'0'}
            elif key_str == 'doctor:2':
                return {b'surname': b'Doctor 3', b'hospital_ID': b'1'}
            elif key_str == 'patient:0':
                return {b'surname': b'Patient 1', b'sex': b'M'}
            elif key_str == 'patient:1':
                return {b'surname': b'Patient 2', b'sex': b'F'}
            elif key_str == 'patient:2':
                return {b'surname': b'Patient 3', b'sex': b'M'}
            elif key_str == 'patient:3':
                return {b'surname': b'Patient 4', b'sex': b'F'}
            elif key_str == 'diagnosis:0':
                return {b'patient_ID': b'0', b'type': b'Flu'}
            elif key_str == 'diagnosis:1':
                return {b'patient_ID': b'1', b'type': b'Cold'}
            return {}
        
        def smembers_side_effect(key):
            key_str = key.decode() if isinstance(key, bytes) else str(key)
            if key_str == 'doctor-patient:0':
                return {b'0', b'1'}
            elif key_str == 'doctor-patient:1':
                return {b'2'}
            return set()
        
        mock_redis.get.side_effect = get_side_effect
        mock_redis.hgetall.side_effect = hgetall_side_effect
        mock_redis.smembers.side_effect = smembers_side_effect
        
        response = self.fetch('/analytics')
        self.assertEqual(response.code, 200)
        
        # Parse JSON response
        import json
        data = json.loads(response.body.decode('utf-8'))
        
        # Check structure
        self.assertIn('summary', data)
        self.assertIn('relationships', data)
        self.assertIn('patient_statistics', data)
        self.assertIn('hospital_statistics', data)
        
        # Check summary
        # Total: 2 hospitals + 3 doctors + 4 patients + 2 diagnoses = 11
        self.assertEqual(data['summary']['total_entities'], 11)
        self.assertEqual(data['summary']['entity_counts']['hospitals'], 2)
        self.assertEqual(data['summary']['entity_counts']['doctors'], 3)
        self.assertEqual(data['summary']['entity_counts']['patients'], 4)
        self.assertEqual(data['summary']['entity_counts']['diagnoses'], 2)

    @patch('main.r')
    def test_get_analytics_empty_database(self, mock_redis):
        """Test analytics when database is empty"""
        mock_redis.get.return_value = b'0'
        mock_redis.hgetall.return_value = {}
        mock_redis.smembers.return_value = set()
        
        response = self.fetch('/analytics')
        self.assertEqual(response.code, 200)
        
        import json
        data = json.loads(response.body.decode('utf-8'))
        
        self.assertEqual(data['summary']['total_entities'], 0)
        self.assertEqual(data['summary']['entity_counts']['hospitals'], 0)

    @patch('main.r')
    def test_get_analytics_redis_connection_error(self, mock_redis):
        """Test analytics when Redis connection fails"""
        mock_redis.get.side_effect = redis.exceptions.ConnectionError()
        
        response = self.fetch('/analytics')
        self.assertEqual(response.code, 400)
        self.assertIn(b'Redis connection refused', response.body)

    @patch('main.r')
    def test_get_stats_brief(self, mock_redis):
        """Test that /stats returns brief statistics (different from /analytics)"""
        def get_side_effect(key):
            key_str = key.decode() if isinstance(key, bytes) else str(key)
            if key_str in ['hospital:autoID', 'doctor:autoID', 'patient:autoID', 'diagnosis:autoID']:
                return b'1'
            elif key_str == 'db_initiated':
                return b'1'
            return None
        
        mock_redis.get.side_effect = get_side_effect
        mock_redis.hgetall.return_value = {}
        mock_redis.smembers.return_value = set()
        
        response = self.fetch('/stats')
        self.assertEqual(response.code, 200)
        
        import json
        data = json.loads(response.body.decode('utf-8'))
        
        # Stats should have brief format, not full analytics
        self.assertIn('total_entities', data)
        self.assertIn('hospitals', data)
        self.assertIn('doctors', data)
        self.assertIn('patients', data)
        self.assertIn('diagnoses', data)
        self.assertIn('doctor_patient_relationships', data)
        self.assertIn('avg_patients_per_doctor', data)
        self.assertIn('avg_diagnoses_per_patient', data)
        
        # Should NOT have detailed sections like analytics
        self.assertNotIn('summary', data)
        self.assertNotIn('relationships', data)
        self.assertNotIn('patient_statistics', data)
        self.assertNotIn('hospital_statistics', data)


if __name__ == '__main__':
    unittest.main()

