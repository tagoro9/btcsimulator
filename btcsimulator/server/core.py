__author__ = 'victor'
from . import app
import logging
from redis import StrictRedis
from flask.ext.socketio import SocketIO
from gevent import Greenlet, monkey
# Connect to redis
r = StrictRedis(host=app.config['REDIS_HOST'], port=app.config['REDIS_PORT'], db=app.config['REDIS_DB'])
# Add socket io capabilites
socketio = SocketIO(app)

monkey.patch_all()

def sub(pubsub):
    # Subscribe to channel
    pubsub.subscribe(app.config['SIMULATOR_NAMESPACE'])
    for message in pubsub.listen():
        # Process new messages when they arrive
        Greenlet.spawn(process_received_mesg, message)

def process_received_mesg(message):
    # Notify all clients the message
    socketio.emit('redis', message['data'], namespace=app.config['SIMULATOR_NAMESPACE'])

pubsub = r.pubsub()
Greenlet.spawn(sub, pubsub)

logger = logging.getLogger("btcsimulator")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(levelname)s: %(message)s","%Y-%m-%d %H:%M:%S")
ch = logging.StreamHandler()
ch.setFormatter(formatter)
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)