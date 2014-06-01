__author__ = 'victor'

from btcsimulator import runserver
from btcsimulator.server.core import celery
from btcsimulator.server.core import logger


if __name__ == '__main__':
    logger.info("Web server running on http://localhost:5000")
    runserver()
