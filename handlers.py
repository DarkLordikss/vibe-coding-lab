#!/usr/bin/env python3
"""
Request handlers for the hospital management system.
"""

import json
import logging
import tornado.web
import redis.exceptions

from database import get_database, RedisKeys


class BaseHandler(tornado.web.RequestHandler):
    """Base handler with common error handling."""
    
    def handle_redis_error(self, error):
        """Handle Redis connection errors."""
        if isinstance(error, redis.exceptions.ConnectionError):
            self.set_status(400)
            self.write("Redis connection refused")
            return True
        return False
    
    def safe_redis_operation(self, operation, error_handler=None):
        """Safely execute a Redis operation with error handling."""
        try:
            return operation()
        except redis.exceptions.ConnectionError as e:
            if error_handler:
                error_handler(e)
            else:
                self.handle_redis_error(e)
            return None
        except Exception as e:
            # Log other exceptions and return error
            logging.error(f"Error in operation: {e}", exc_info=True)
            self.set_status(500)
            self.write(f"Internal server error: {str(e)}")
            return None


class MainHandler(BaseHandler):
    """Handler for the main page."""
    
    def get(self):
        self.render('templates/index.html')


class HospitalHandler(BaseHandler):
    """Handler for hospital operations."""
    
    def get(self):
        items = []
        
        def operation():
            db = get_database()
            return db.get_all_entities("hospital")
        
        result = self.safe_redis_operation(operation)
        if result is not None:
            items = result
            self.render('templates/hospital.html', items=items)
    
    def post(self):
        name = self.get_argument('name', '')
        address = self.get_argument('address', '')
        beds_number = self.get_argument('beds_number', '')
        phone = self.get_argument('phone', '')
        
        if not name or not address:
            self.set_status(400)
            self.write("Hospital name and address required")
            return
        
        logging.debug(f'{name} {address} {beds_number} {phone}')
        
        def operation():
            db = get_database()
            entity_id = db.get_auto_id("hospital")
            if not entity_id:
                raise ValueError("Auto ID not found")
            
            fields = {
                'name': name,
                'address': address,
                'phone': phone,
                'beds_number': beds_number
            }
            
            total_set = db.create_entity("hospital", entity_id, fields)
            db.increment_auto_id("hospital")
            
            return entity_id, total_set
        
        result = self.safe_redis_operation(operation)
        if result is not None:
            entity_id, total_set = result
            if total_set != 4:
                self.set_status(500)
                self.write("Something went terribly wrong")
            else:
                self.write(f'OK: ID {entity_id} for {name}')


class DoctorHandler(BaseHandler):
    """Handler for doctor operations."""
    
    def get(self):
        items = []
        
        def operation():
            db = get_database()
            return db.get_all_entities("doctor")
        
        result = self.safe_redis_operation(operation)
        if result is not None:
            items = result
            self.render('templates/doctor.html', items=items)
    
    def post(self):
        surname = self.get_argument('surname', '')
        profession = self.get_argument('profession', '')
        hospital_ID = self.get_argument('hospital_ID', '')
        
        if not surname or not profession:
            self.set_status(400)
            self.write("Surname and profession required")
            return
        
        logging.debug(f'{surname} {profession}')
        
        def operation():
            db = get_database()
            if hospital_ID:
                # Check that hospital exists
                hospital = db.get_entity("hospital", hospital_ID)
                if not hospital:
                    return None, None, "No hospital with such ID"
            
            entity_id = db.get_auto_id("doctor")
            if not entity_id:
                raise ValueError("Auto ID not found")
            
            fields = {
                'surname': surname,
                'profession': profession,
                'hospital_ID': hospital_ID
            }
            
            total_set = db.create_entity("doctor", entity_id, fields)
            db.increment_auto_id("doctor")
            
            return entity_id, total_set, None
        
        result = self.safe_redis_operation(operation)
        if result is not None:
            entity_id, total_set, error_msg = result
            if error_msg:
                self.set_status(400)
                self.write(error_msg)
            elif total_set != 3:
                self.set_status(500)
                self.write("Something went terribly wrong")
            else:
                self.write(f'OK: ID {entity_id} for {surname}')


class PatientHandler(BaseHandler):
    """Handler for patient operations."""
    
    def get(self):
        items = []
        
        def operation():
            db = get_database()
            return db.get_all_entities("patient")
        
        result = self.safe_redis_operation(operation)
        if result is not None:
            items = result
            self.render('templates/patient.html', items=items)
    
    def post(self):
        surname = self.get_argument('surname', '')
        born_date = self.get_argument('born_date', '')
        sex = self.get_argument('sex', '')
        mpn = self.get_argument('mpn', '')
        
        if not surname or not born_date or not sex or not mpn:
            self.set_status(400)
            self.write("All fields required")
            return
        
        # Validate sex field
        if sex not in ['M', 'F']:
            self.set_status(400)
            self.write("Sex must be 'M' or 'F'")
            return
        
        logging.debug(f'{surname} {born_date} {sex} {mpn}')
        
        def operation():
            db = get_database()
            entity_id = db.get_auto_id("patient")
            if not entity_id:
                raise ValueError("Auto ID not found")
            
            fields = {
                'surname': surname,
                'born_date': born_date,
                'sex': sex,
                'mpn': mpn
            }
            
            total_set = db.create_entity("patient", entity_id, fields)
            db.increment_auto_id("patient")
            
            return entity_id, total_set
        
        result = self.safe_redis_operation(operation)
        if result is not None:
            entity_id, total_set = result
            if total_set != 4:
                self.set_status(500)
                self.write("Something went terribly wrong")
            else:
                self.write(f'OK: ID {entity_id} for {surname}')


class DiagnosisHandler(BaseHandler):
    """Handler for diagnosis operations."""
    
    def get(self):
        items = []
        
        def operation():
            db = get_database()
            return db.get_all_entities("diagnosis")
        
        result = self.safe_redis_operation(operation)
        if result is not None:
            items = result
            self.render('templates/diagnosis.html', items=items)
    
    def post(self):
        patient_ID = self.get_argument('patient_ID', '')
        diagnosis_type = self.get_argument('type', '')
        information = self.get_argument('information', '')
        
        if not patient_ID or not diagnosis_type:
            self.set_status(400)
            self.write("Patiend ID and diagnosis type required")
            return
        
        logging.debug(f'{patient_ID} {diagnosis_type} {information}')
        
        def operation():
            db = get_database()
            patient = db.get_entity("patient", patient_ID)
            if not patient:
                return None, None, None, "No patient with such ID"
            
            entity_id = db.get_auto_id("diagnosis")
            if not entity_id:
                raise ValueError("Auto ID not found")
            
            fields = {
                'patient_ID': patient_ID,
                'type': diagnosis_type,
                'information': information
            }
            
            total_set = db.create_entity("diagnosis", entity_id, fields)
            db.increment_auto_id("diagnosis")
            
            return entity_id, total_set, patient, None
        
        result = self.safe_redis_operation(operation)
        if result is not None:
            entity_id, total_set, patient, error_msg = result
            if error_msg:
                self.set_status(400)
                self.write(error_msg)
            elif total_set != 3:
                self.set_status(500)
                self.write("Something went terribly wrong")
            else:
                patient_surname = patient[b'surname'].decode() if isinstance(patient.get(b'surname'), bytes) else patient.get('surname', '')
                self.write(f'OK: ID {entity_id} for patient {patient_surname}')


class DoctorPatientHandler(BaseHandler):
    """Handler for doctor-patient relationship operations."""
    
    def get(self):
        items = {}
        
        def operation():
            db = get_database()
            doctor_auto_id = db.get_auto_id("doctor")
            if not doctor_auto_id:
                return {}
            
            result_items = {}
            for i in range(int(doctor_auto_id)):
                set_key = RedisKeys.doctor_patient_key(str(i))
                result = db.get_set_members(set_key)
                if result:
                    result_items[i] = result
            
            return result_items
        
        result = self.safe_redis_operation(operation)
        if result is not None:
            items = result
            self.render('templates/doctor-patient.html', items=items)
    
    def post(self):
        doctor_ID = self.get_argument('doctor_ID', '')
        patient_ID = self.get_argument('patient_ID', '')
        
        if not doctor_ID or not patient_ID:
            self.set_status(400)
            self.write("ID required")
            return
        
        logging.debug(f'{doctor_ID} {patient_ID}')
        
        def operation():
            db = get_database()
            patient = db.get_entity("patient", patient_ID)
            doctor = db.get_entity("doctor", doctor_ID)
            
            if not patient or not doctor:
                return "No such ID for doctor or patient"
            
            set_key = RedisKeys.doctor_patient_key(doctor_ID)
            db.add_to_set(set_key, patient_ID)
            
            return True  # Return True on success
        
        result = self.safe_redis_operation(operation)
        if result is not None:
            if isinstance(result, str):
                # Error message
                self.set_status(400)
                self.write(result)
            elif result is True:
                # Success
                self.write(f"OK: doctor ID: {doctor_ID}, patient ID: {patient_ID}")
        # If result is None, Redis connection error was already handled


class AnalyticsHandler(BaseHandler):
    """Handler for comprehensive analytics about the system."""
    
    def get(self):
        """Get comprehensive analytics about the system."""
        def operation():
            db = get_database()
            
            # Get entity counts
            hospitals_count = db.count_entities("hospital")
            doctors_count = db.count_entities("doctor")
            patients_count = db.count_entities("patient")
            diagnoses_count = db.count_entities("diagnosis")
            
            total_entities = hospitals_count + doctors_count + patients_count + diagnoses_count
            
            # Get relationship statistics
            doctor_patient_stats = db.get_patients_per_doctor_stats()
            patient_diagnosis_stats = db.get_diagnoses_per_patient_stats()
            
            # Get patient statistics
            patient_sex_distribution = db.get_patient_sex_distribution()
            
            # Get hospital statistics
            hospital_statistics = db.get_hospital_statistics()
            
            analytics = {
                "summary": {
                    "total_entities": total_entities,
                    "entity_counts": {
                        "hospitals": hospitals_count,
                        "doctors": doctors_count,
                        "patients": patients_count,
                        "diagnoses": diagnoses_count
                    }
                },
                "relationships": {
                    "doctor_patient": doctor_patient_stats,
                    "patient_diagnosis": patient_diagnosis_stats
                },
                "patient_statistics": {
                    "sex_distribution": patient_sex_distribution
                },
                "hospital_statistics": hospital_statistics
            }
            
            return analytics
        
        result = self.safe_redis_operation(operation)
        if result is not None:
            self.set_header("Content-Type", "application/json")
            self.write(json.dumps(result, indent=2, ensure_ascii=False))


class StatsHandler(BaseHandler):
    """Handler for brief statistics about the system."""
    
    def get(self):
        """Get brief statistics - only key metrics."""
        def operation():
            db = get_database()
            
            # Get only basic counts
            hospitals_count = db.count_entities("hospital")
            doctors_count = db.count_entities("doctor")
            patients_count = db.count_entities("patient")
            diagnoses_count = db.count_entities("diagnosis")
            
            total_entities = hospitals_count + doctors_count + patients_count + diagnoses_count
            
            # Get only key relationship metrics
            doctor_patient_stats = db.get_patients_per_doctor_stats()
            patient_diagnosis_stats = db.get_diagnoses_per_patient_stats()
            
            stats = {
                "total_entities": total_entities,
                "hospitals": hospitals_count,
                "doctors": doctors_count,
                "patients": patients_count,
                "diagnoses": diagnoses_count,
                "doctor_patient_relationships": doctor_patient_stats.get("total_relationships", 0),
                "avg_patients_per_doctor": doctor_patient_stats.get("avg_patients_per_doctor", 0.0),
                "avg_diagnoses_per_patient": patient_diagnosis_stats.get("avg_diagnoses_per_patient", 0.0)
            }
            
            return stats
        
        result = self.safe_redis_operation(operation)
        if result is not None:
            self.set_header("Content-Type", "application/json")
            self.write(json.dumps(result, indent=2, ensure_ascii=False))

