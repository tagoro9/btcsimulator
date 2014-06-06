__author__ = 'victor'

REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0
SECRET_KEY = 'is it necessary?'
SIMULATOR_NAMESPACE = "/btcsimulator"
CELERY_BROKER_URL='redis://localhost:6379/0'
CELERY_RESULT_BACKEND='redis://localhost:6379/0'