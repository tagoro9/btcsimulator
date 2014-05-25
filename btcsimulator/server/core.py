__author__ = 'victor'
from . import app
import logging
from redis import StrictRedis
from flask.ext.socketio import SocketIO
from gevent import Greenlet, monkey
from datetime import timedelta
from flask import make_response, request, current_app
from functools import update_wrapper
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

# Create application logger
logger = logging.getLogger("btcsimulator")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(levelname)s: %(message)s","%Y-%m-%d %H:%M:%S")
ch = logging.StreamHandler()
ch.setFormatter(formatter)
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)

# Create cross domain decorator to add HTTP origin headers
def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator