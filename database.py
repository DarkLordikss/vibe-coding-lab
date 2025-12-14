#!/usr/bin/env python3
"""
Database module for Redis operations.
Provides abstraction layer for data access.
"""

import os
import redis


# Redis key prefixes
class RedisKeys:
    """Constants for Redis keys."""
    HOSPITAL_AUTO_ID = "hospital:autoID"
    DOCTOR_AUTO_ID = "doctor:autoID"
    PATIENT_AUTO_ID = "patient:autoID"
    DIAGNOSIS_AUTO_ID = "diagnosis:autoID"
    DB_INITIATED = "db_initiated"
    
    @staticmethod
    def hospital_key(hospital_id):
        return f"hospital:{hospital_id}"
    
    @staticmethod
    def doctor_key(doctor_id):
        return f"doctor:{doctor_id}"
    
    @staticmethod
    def patient_key(patient_id):
        return f"patient:{patient_id}"
    
    @staticmethod
    def diagnosis_key(diagnosis_id):
        return f"diagnosis:{diagnosis_id}"
    
    @staticmethod
    def doctor_patient_key(doctor_id):
        return f"doctor-patient:{doctor_id}"


class Database:
    """Database abstraction for Redis operations."""
    
    def __init__(self, redis_client):
        """Initialize with a Redis client."""
        self.redis = redis_client
    
    def get_auto_id(self, entity_type):
        """Get current auto ID for an entity type."""
        key = getattr(RedisKeys, f"{entity_type.upper()}_AUTO_ID")
        value = self.redis.get(key)
        if value is None:
            return None
        return value.decode() if isinstance(value, bytes) else value
    
    def increment_auto_id(self, entity_type):
        """Increment auto ID for an entity type."""
        key = getattr(RedisKeys, f"{entity_type.upper()}_AUTO_ID")
        return self.redis.incr(key)
    
    def get_all_entities(self, entity_type):
        """Get all entities of a given type."""
        auto_id = self.get_auto_id(entity_type)
        if not auto_id:
            return []
        
        items = []
        key_func = getattr(RedisKeys, f"{entity_type.lower()}_key")
        
        for i in range(int(auto_id)):
            result = self.redis.hgetall(key_func(str(i)))
            if result:
                items.append(result)
        
        return items
    
    def get_entity(self, entity_type, entity_id):
        """Get a single entity by ID."""
        key_func = getattr(RedisKeys, f"{entity_type.lower()}_key")
        return self.redis.hgetall(key_func(entity_id))
    
    def create_entity(self, entity_type, entity_id, fields):
        """Create an entity with given fields."""
        key_func = getattr(RedisKeys, f"{entity_type.lower()}_key")
        key = key_func(entity_id)
        
        total_set = 0
        for field_name, field_value in fields.items():
            total_set += self.redis.hset(key, field_name, field_value)
        
        return total_set
    
    def add_to_set(self, set_key, value):
        """Add value to a Redis set."""
        return self.redis.sadd(set_key, value)
    
    def get_set_members(self, set_key):
        """Get all members of a Redis set."""
        return self.redis.smembers(set_key)
    
    def set_initial_auto_id(self, entity_type, value=1):
        """Set initial auto ID value."""
        key = getattr(RedisKeys, f"{entity_type.upper()}_AUTO_ID")
        return self.redis.set(key, value)
    
    def is_db_initialized(self):
        """Check if database is initialized."""
        return self.redis.get(RedisKeys.DB_INITIATED) is not None
    
    def mark_db_initialized(self):
        """Mark database as initialized."""
        return self.redis.set(RedisKeys.DB_INITIATED, 1)
    
    def count_entities(self, entity_type):
        """Count entities of a given type."""
        items = self.get_all_entities(entity_type)
        return len(items)
    
    def get_patients_per_doctor_stats(self):
        """Get statistics about patients per doctor."""
        doctor_auto_id = self.get_auto_id("doctor")
        if not doctor_auto_id:
            return {
                "total_relationships": 0,
                "doctors_with_patients": 0,
                "total_doctors": 0,
                "avg_patients_per_doctor": 0.0
            }
        
        total_relationships = 0
        doctors_with_patients = 0
        
        for i in range(int(doctor_auto_id)):
            set_key = RedisKeys.doctor_patient_key(str(i))
            patients = self.get_set_members(set_key)
            if patients:
                doctors_with_patients += 1
                total_relationships += len(patients)
        
        total_doctors = self.count_entities("doctor")
        avg_patients = total_relationships / total_doctors if total_doctors > 0 else 0.0
        
        return {
            "total_relationships": total_relationships,
            "doctors_with_patients": doctors_with_patients,
            "total_doctors": total_doctors,
            "avg_patients_per_doctor": round(avg_patients, 2)
        }
    
    def get_diagnoses_per_patient_stats(self):
        """Get statistics about diagnoses per patient."""
        total_diagnoses = self.count_entities("diagnosis")
        total_patients = self.count_entities("patient")
        
        # Count unique patients with diagnoses
        diagnoses = self.get_all_entities("diagnosis")
        patients_with_diagnoses = set()
        for diagnosis in diagnoses:
            patient_id = diagnosis.get(b'patient_ID', b'').decode() if isinstance(diagnosis.get(b'patient_ID'), bytes) else diagnosis.get('patient_ID', '')
            if patient_id:
                patients_with_diagnoses.add(patient_id)
        
        avg_diagnoses = total_diagnoses / total_patients if total_patients > 0 else 0.0
        
        return {
            "total_diagnoses": total_diagnoses,
            "patients_with_diagnoses": len(patients_with_diagnoses),
            "total_patients": total_patients,
            "avg_diagnoses_per_patient": round(avg_diagnoses, 2)
        }
    
    def get_patient_sex_distribution(self):
        """Get distribution of patients by sex."""
        patients = self.get_all_entities("patient")
        total = len(patients)
        male = 0
        female = 0
        
        for patient in patients:
            sex = patient.get(b'sex', b'').decode() if isinstance(patient.get(b'sex'), bytes) else patient.get('sex', '')
            if sex == 'M':
                male += 1
            elif sex == 'F':
                female += 1
        
        male_percentage = (male / total * 100) if total > 0 else 0.0
        female_percentage = (female / total * 100) if total > 0 else 0.0
        
        return {
            "total": total,
            "male": male,
            "female": female,
            "male_percentage": round(male_percentage, 2),
            "female_percentage": round(female_percentage, 2)
        }
    
    def get_hospital_statistics(self):
        """Get detailed statistics for each hospital."""
        hospitals = self.get_all_entities("hospital")
        doctors = self.get_all_entities("doctor")
        
        # Count doctors per hospital
        hospital_doctors = {}
        for doctor in doctors:
            hospital_id = doctor.get(b'hospital_ID', b'').decode() if isinstance(doctor.get(b'hospital_ID'), bytes) else doctor.get('hospital_ID', '')
            if hospital_id:
                hospital_doctors[hospital_id] = hospital_doctors.get(hospital_id, 0) + 1
        
        result = []
        for i, hospital in enumerate(hospitals):
            hospital_id = str(i)
            name = hospital.get(b'name', b'').decode() if isinstance(hospital.get(b'name'), bytes) else hospital.get('name', '')
            beds = hospital.get(b'beds_number', b'').decode() if isinstance(hospital.get(b'beds_number'), bytes) else hospital.get('beds_number', '')
            
            result.append({
                "id": hospital_id,
                "name": name,
                "beds_number": beds,
                "doctors_count": hospital_doctors.get(hospital_id, 0)
            })
        
        return result


def get_redis_client():
    """Create and return a Redis client."""
    host = os.environ.get("REDIS_HOST", "localhost")
    port = int(os.environ.get("REDIS_PORT", "6379"))
    return redis.StrictRedis(host=host, port=port, db=0)


# Global Redis client for backward compatibility with tests
# This will be set from main.py to maintain test compatibility
r = None

# Global database instance (will be initialized after r is set)
db = None

def initialize_database(redis_client=None):
    """Initialize global database instance."""
    global r, db
    if redis_client is not None:
        r = redis_client
    elif r is None:
        r = get_redis_client()
    db = Database(r)

def get_database():
    """Get the global database instance, initializing if necessary."""
    global r, db
    # Check if main.r exists (for test compatibility)
    # Always prefer main.r if it exists (important for tests with mocks)
    redis_client = None
    main_r_exists = False
    try:
        import main
        if hasattr(main, 'r') and main.r is not None:
            redis_client = main.r
            main_r_exists = True
    except (ImportError, AttributeError):
        pass
    
    if redis_client is None:
        redis_client = r if r is not None else get_redis_client()
    
    # Always recreate db if it doesn't exist
    if db is None:
        db = Database(redis_client)
    # If main.r exists, always use it (important for tests where mocks change)
    elif main_r_exists and db.redis is not redis_client:
        db = Database(redis_client)
    # Otherwise, only recreate if redis client changed
    elif not main_r_exists and db.redis is not redis_client:
        db = Database(redis_client)
    
    return db

