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
    try:
        import main
        if hasattr(main, 'r') and main.r is not None:
            redis_client = main.r
        else:
            redis_client = r if r is not None else get_redis_client()
    except (ImportError, AttributeError):
        redis_client = r if r is not None else get_redis_client()
    
    if db is None or db.redis is not redis_client:
        db = Database(redis_client)
    return db

