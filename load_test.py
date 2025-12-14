#!/usr/bin/env python3
"""
Load test script for the hospital management system using Locust.
Tests all endpoints with realistic user behavior patterns.

Usage:
    locust -f load_test.py --host=http://localhost:8888
    
    Or with custom parameters:
    locust -f load_test.py --host=http://localhost:8888 --users=100 --spawn-rate=10
"""

import random
import re
from locust import HttpUser, task, between


class HospitalSystemUser(HttpUser):
    """Simulates a user interacting with the hospital management system."""
    
    wait_time = between(1, 3)  # Wait 1-3 seconds between requests
    
    def on_start(self):
        """Called when a simulated user starts. Initialize some test data."""
        self.hospital_ids = []
        self.doctor_ids = []
        self.patient_ids = []
        self.diagnosis_ids = []
        
        # Create initial test data for relationships
        self._create_initial_data()
    
    def _extract_id(self, response_text):
        """Extract ID from response text (format: 'OK: ID X for ...')."""
        try:
            match = re.search(r'ID (\d+)', response_text)
            if match:
                return match.group(1)
        except (AttributeError, IndexError):
            pass
        return None
    
    def _create_initial_data(self):
        """Create some initial test data for relationships."""
        # Create a hospital
        hospital_data = {
            'name': f'Test Hospital {random.randint(1000, 9999)}',
            'address': f'{random.randint(1, 999)} Test Street',
            'beds_number': str(random.randint(50, 500)),
            'phone': f'+1{random.randint(1000000000, 9999999999)}'
        }
        with self.client.post('/hospital', data=hospital_data, catch_response=True) as response:
            if response.status_code == 200:
                hospital_id = self._extract_id(response.text)
                if hospital_id:
                    self.hospital_ids.append(hospital_id)
            elif response.status_code == 400:
                response.failure("Redis connection refused or validation error")
        
        # Create a patient
        patient_data = {
            'surname': f'Patient{random.randint(1000, 9999)}',
            'born_date': f'{random.randint(1950, 2000)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}',
            'sex': random.choice(['M', 'F']),
            'mpn': str(random.randint(100000, 999999))
        }
        with self.client.post('/patient', data=patient_data, catch_response=True) as response:
            if response.status_code == 200:
                patient_id = self._extract_id(response.text)
                if patient_id:
                    self.patient_ids.append(patient_id)
            elif response.status_code == 400:
                response.failure("Redis connection refused or validation error")
    
    # GET requests - viewing data (more frequent)
    @task(5)
    def view_main_page(self):
        """View the main page - most common action."""
        with self.client.get("/", catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"Failed to load main page: {response.status_code}")
    
    @task(4)
    def view_hospitals(self):
        """View list of hospitals."""
        with self.client.get("/hospital", catch_response=True) as response:
            if response.status_code == 400:
                response.failure("Redis connection refused")
            elif response.status_code != 200:
                response.failure(f"Failed to load hospitals: {response.status_code}")
    
    @task(4)
    def view_doctors(self):
        """View list of doctors."""
        with self.client.get("/doctor", catch_response=True) as response:
            if response.status_code == 400:
                response.failure("Redis connection refused")
            elif response.status_code != 200:
                response.failure(f"Failed to load doctors: {response.status_code}")
    
    @task(4)
    def view_patients(self):
        """View list of patients."""
        with self.client.get("/patient", catch_response=True) as response:
            if response.status_code == 400:
                response.failure("Redis connection refused")
            elif response.status_code != 200:
                response.failure(f"Failed to load patients: {response.status_code}")
    
    @task(3)
    def view_diagnoses(self):
        """View list of diagnoses."""
        with self.client.get("/diagnosis", catch_response=True) as response:
            if response.status_code == 400:
                response.failure("Redis connection refused")
            elif response.status_code != 200:
                response.failure(f"Failed to load diagnoses: {response.status_code}")
    
    @task(2)
    def view_doctor_patient_relations(self):
        """View doctor-patient relationships."""
        with self.client.get("/doctor-patient", catch_response=True) as response:
            if response.status_code == 400:
                response.failure("Redis connection refused")
            elif response.status_code != 200:
                response.failure(f"Failed to load doctor-patient relations: {response.status_code}")
    
    # POST requests - creating data (less frequent)
    @task(3)
    def create_hospital(self):
        """Create a new hospital."""
        data = {
            'name': f'Hospital {random.randint(1000, 9999)}',
            'address': f'{random.randint(1, 999)} Main Street',
            'beds_number': str(random.randint(50, 500)),
            'phone': f'+1{random.randint(1000000000, 9999999999)}'
        }
        with self.client.post('/hospital', data=data, catch_response=True) as response:
            if response.status_code == 200:
                hospital_id = self._extract_id(response.text)
                if hospital_id:
                    self.hospital_ids.append(hospital_id)
                else:
                    response.failure("Failed to extract hospital ID from response")
            elif response.status_code == 400:
                response.failure("Validation error or Redis connection refused")
            elif response.status_code == 500:
                response.failure("Server error creating hospital")
            else:
                response.failure(f"Unexpected status code: {response.status_code}")
    
    @task(3)
    def create_doctor(self):
        """Create a new doctor."""
        hospital_id = random.choice(self.hospital_ids) if self.hospital_ids else ''
        data = {
            'surname': f'Dr. {random.choice(["Smith", "Johnson", "Williams", "Brown", "Jones", "Davis", "Miller", "Wilson"])}',
            'profession': random.choice(['Surgeon', 'Physician', 'Cardiologist', 'Neurologist', 'Pediatrician', 'Dermatologist', 'Orthopedist']),
            'hospital_ID': hospital_id
        }
        with self.client.post('/doctor', data=data, catch_response=True) as response:
            if response.status_code == 200:
                doctor_id = self._extract_id(response.text)
                if doctor_id:
                    self.doctor_ids.append(doctor_id)
                else:
                    response.failure("Failed to extract doctor ID from response")
            elif response.status_code == 400:
                response.failure("Validation error or Redis connection refused")
            elif response.status_code == 500:
                response.failure("Server error creating doctor")
            else:
                response.failure(f"Unexpected status code: {response.status_code}")
    
    @task(3)
    def create_patient(self):
        """Create a new patient."""
        data = {
            'surname': f'Patient{random.randint(1000, 9999)}',
            'born_date': f'{random.randint(1950, 2000)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}',
            'sex': random.choice(['M', 'F']),
            'mpn': str(random.randint(100000, 999999))
        }
        with self.client.post('/patient', data=data, catch_response=True) as response:
            if response.status_code == 200:
                patient_id = self._extract_id(response.text)
                if patient_id:
                    self.patient_ids.append(patient_id)
                else:
                    response.failure("Failed to extract patient ID from response")
            elif response.status_code == 400:
                response.failure("Validation error or Redis connection refused")
            elif response.status_code == 500:
                response.failure("Server error creating patient")
            else:
                response.failure(f"Unexpected status code: {response.status_code}")
    
    @task(2)
    def create_diagnosis(self):
        """Create a new diagnosis."""
        if not self.patient_ids:
            return
        
        patient_id = random.choice(self.patient_ids)
        data = {
            'patient_ID': patient_id,
            'type': random.choice(['Flu', 'Cold', 'Fever', 'Headache', 'Injury', 'Checkup', 'Hypertension', 'Diabetes']),
            'information': f'Patient diagnosis information {random.randint(1, 1000)}'
        }
        with self.client.post('/diagnosis', data=data, catch_response=True) as response:
            if response.status_code == 200:
                diagnosis_id = self._extract_id(response.text)
                if diagnosis_id:
                    self.diagnosis_ids.append(diagnosis_id)
            elif response.status_code == 400:
                response.failure("Validation error or Redis connection refused")
            elif response.status_code == 500:
                response.failure("Server error creating diagnosis")
            else:
                response.failure(f"Unexpected status code: {response.status_code}")
    
    @task(2)
    def create_doctor_patient_relation(self):
        """Create a doctor-patient relationship."""
        if not self.doctor_ids or not self.patient_ids:
            return
        
        doctor_id = random.choice(self.doctor_ids)
        patient_id = random.choice(self.patient_ids)
        data = {
            'doctor_ID': doctor_id,
            'patient_ID': patient_id
        }
        with self.client.post('/doctor-patient', data=data, catch_response=True) as response:
            if response.status_code == 200:
                pass  # Success
            elif response.status_code == 400:
                response.failure("Validation error or Redis connection refused")
            else:
                response.failure(f"Unexpected status code: {response.status_code}")

