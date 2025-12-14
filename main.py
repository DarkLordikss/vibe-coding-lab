#!/usr/bin/env python3

import logging
import os
import redis
import tornado.ioloop
import tornado.web

from tornado.options import parse_command_line

# Import handlers and database
from handlers import (
    MainHandler, HospitalHandler, DoctorHandler, 
    PatientHandler, DiagnosisHandler, DoctorPatientHandler
)
from database import initialize_database, RedisKeys

PORT = 8888

# Global Redis client for backward compatibility with tests
# This must be defined before importing database module
r = redis.StrictRedis(host=os.environ.get("REDIS_HOST", "localhost"), 
    port=int(os.environ.get("REDIS_PORT", "6379")), db=0)

# Initialize database with the Redis client (lazy initialization in get_database)
# Don't initialize here to allow tests to mock r first


# Handlers are now imported from handlers.py module


def init_db():
    """Initialize database with default values."""
    from database import get_database
    db = get_database()
    if not db.is_db_initialized():
        db.set_initial_auto_id("hospital", 1)
        db.set_initial_auto_id("doctor", 1)
        db.set_initial_auto_id("patient", 1)
        db.set_initial_auto_id("diagnosis", 1)
        db.mark_db_initialized()


def make_app(autoreload=None, debug=None, serve_traceback=None):
    """Create and return a Tornado web application.
    
    Args:
        autoreload: Enable autoreload (default: True if not in test mode)
        debug: Enable debug mode (default: True if not in test mode)
        serve_traceback: Show traceback in error responses (default: True if not in test mode)
    """
    if autoreload is None:
        autoreload = os.environ.get('TORNADO_AUTORELOAD', 'True').lower() == 'true'
    if debug is None:
        debug = os.environ.get('TORNADO_DEBUG', 'True').lower() == 'true'
    if serve_traceback is None:
        serve_traceback = os.environ.get('TORNADO_SERVE_TRACEBACK', 'True').lower() == 'true'
    
    return tornado.web.Application([
        (r"/", MainHandler),
        (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': 'static/'}),
        (r"/hospital", HospitalHandler),
        (r"/doctor", DoctorHandler),
        (r"/patient", PatientHandler),
        (r"/diagnosis", DiagnosisHandler),
        (r"/doctor-patient", DoctorPatientHandler)
    ], autoreload=autoreload, debug=debug, compiled_template_cache=False, serve_traceback=serve_traceback)


if __name__ == "__main__":
    init_db()
    app = make_app()
    app.listen(PORT)
    tornado.options.parse_command_line()
    logging.info("Listening on " + str(PORT))
    tornado.ioloop.IOLoop.current().start()