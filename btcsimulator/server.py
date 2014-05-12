__author__ = 'victor'

from gevent import Greenlet, monkey
from redis import StrictRedis
from flask import Flask, render_template, jsonify
from flask.ext.socketio import SocketIO, emit
from btcsimulator import Simulator
import json
import logging

monkey.patch_all()

# Create flask app
app = Flask(__name__)
# Configure flask app
app.config['SECRET_KEY'] = 'is it necessary?'
# Add socket io capabilites
socketio = SocketIO(app)
# Connect to redis
r = StrictRedis(host='localhost', port=6379, db=0)
# Define main namespace
SIMULATOR_NAMESPACE = "/btcsimulator"

# This class will allow to receive any redis message published in certain channel
class RedisLiveData:
    def __init__(self, channel_name):
        # Store channel name and redis connection
        self.channel_name = channel_name
        self.redis_conn = r
        # Start listening for messages
        pubsub = self.redis_conn.pubsub()
        Greenlet.spawn(self.sub, pubsub)

    def sub(self, pubsub):
        # Subscribe to channel
        pubsub.subscribe(self.channel_name)
        for message in pubsub.listen():
            # Process new messages when they arrive
            Greenlet.spawn(self.process_rcvd_mesg, message)

    def process_rcvd_mesg(self, message):
        # Notify all clients the message
        socketio.emit('my response', message['data'], namespace=self.channel_name)

@app.route('/')
def index():
    return "Hello world!"

@app.route('/miners', methods=['GET'])
def miners():
    miners = r.smembers("miners")
    minersData = []
    for miner in miners:
        data = r.hgetall("miners:" + miner)
        data['id'] = miner
        data['blocks'] = list(r.smembers("miners:" + miner + ":blocks"))
        data['links'] = list(r.smembers("miners:" + miner + ":links"))
        minersData.append(data)
    return jsonify(miners=minersData)

@app.route('/chain/<string:head>')
def chain(head):
    data = []
    while head != None:
        data.append(head)
        prev = r.hget("blocks:" + head, "prev")
        head = prev
    return jsonify(chain=data)

@app.route('/summary')
def summary():
    data = dict()
    data['miners'] = r.scard("miners")
    data['links'] = r.scard("links")
    data['blocks'] = r.scard("blocks")
    return jsonify(summary=data)


@socketio.on('my event', namespace=SIMULATOR_NAMESPACE)
def test_message(message):
    emit('my response', {'data': message['data']})

@socketio.on('controls:start', namespace=SIMULATOR_NAMESPACE)
def start(message):
    sim = Simulator()
    emit('log', {'data': message}, broadcast=True)
    sim.start()


@socketio.on('connect', namespace=SIMULATOR_NAMESPACE)
def test_connect():
    logger.info("Client connected")
    emit('my response', {'data': 'Connected'})

@socketio.on('disconnect', namespace=SIMULATOR_NAMESPACE)
def test_disconnect():
    print('Client disconnected')

logger = logging.getLogger("btcsimulator")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(levelname)s: %(message)s","%Y-%m-%d %H:%M:%S")
ch = logging.StreamHandler()
ch.setFormatter(formatter)
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)


if __name__ == '__main__':
    logger.info("Web server running on http://localhost:5000")
    # Subscribe to redis events
    g = RedisLiveData(SIMULATOR_NAMESPACE)
    # Launch socketio web server
    socketio.run(app)