__author__ = 'victor'
from server import app
from server.pubsub import start_pubsub
from server.core import logger


def runserver():
    server = start_pubsub()
    server.run(app)