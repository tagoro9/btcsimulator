__author__ = 'victor'
from server import app
from server.core import socketio, logger

def runserver():
    socketio.run(app)

if __name__ == '__main__':
    logger.info("Web server running on http://localhost:5000")
    runserver()