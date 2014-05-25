__author__ = 'victor'

from gevent import Greenlet, monkey
from redis import StrictRedis
from flask import Flask, render_template, jsonify, make_response
from flask.ext.socketio import SocketIO, emit
from btcsimulator.simulator.btcsimulator import Miner
import logging
from zato.redis_paginator import ZSetPaginator

monkey.patch_all()

# Create flask app
app = Flask(__name__, static_url_path='', static_folder='app/dist')
# Configure flask app
app.url_map.strict_slashes = False
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
    return app.send_static_file('index.html')

def get_block(id):
    block_data = r.hgetall("blocks:" + id)
    block_data['hash'] = id
    return block_data

def get_event(id):
    event_data = r.hgetall("events:" + id)
    event_data['id'] = id
    Miner.BLOCK_REQUEST, Miner.BLOCK_RESPONSE, Miner.BLOCK_NEW, Miner.HEAD_NEW
    if event_data['action'] == str(Miner.BLOCK_REQUEST):
        event_data['action'] = "BLOCK_REQUEST"
    elif event_data['action'] == str(Miner.BLOCK_RESPONSE):
        event_data['action'] = "BLOCK_RESPONSE"
    elif event_data['action'] == str(Miner.BLOCK_NEW):
        event_data['action'] = "BLOCK_NEW"
    elif event_data['action'] == str(Miner.HEAD_NEW):
        event_data['action'] = "HEAD_NEW"
    elif event_data['action'] == str(Miner.ACK):
        event_data['action'] = "ACK"
    return event_data

def get_blocks(key, page):
    items = ZSetPaginator(r, key, 20)
    item_page = items.page(page)
    data = {'count': items.count, 'pages': items.num_pages, 'current': item_page.number, 'data': []}
    for item in item_page.object_list: data['data'].append(get_block(item))
    return data

def get_events(key, page):
    items = ZSetPaginator(r, key, 20)
    item_page = items.page(page)
    data = {'count': items.count, 'pages': items.num_pages, 'current': item_page.number, 'data': []}
    for item in item_page.object_list: data['data'].append(get_event(item))
    return data

@app.route('/miners/<string:id>/blocks', methods=['GET'], defaults={'page': 1})
@app.route('/miners/<string:id>/blocks/page/<int:page>')
def miner_blocks(id, page):
    return jsonify(blocks=get_blocks("miners:" + id + ":blocks", page))

@app.route('/miners/<string:id>/blocks-mined', methods=['GET'], defaults={'page': 1})
@app.route('/miners/<string:id>/blocks-mined/page/<int:page>', methods=['GET'])
def miner_blocks_mined(id, page):
    return jsonify(blocks=get_blocks("miners:" + id + ":blocks-mined", page))

@app.route('/blocks', methods=['GET'], defaults={'page': 1})
@app.route('/blocks/page/<page>', methods=['GET'])
def blocks(page):
    return jsonify(blocks=get_blocks("blocks", page))

@app.route('/blocks/<string:id>', methods=['GET'])
def block(id):
    block = r.hgetall("blocks:" + id)
    block['hash'] = id
    return jsonify(block=block)

@app.route('/events', methods=['GET'], defaults={'page': 1})
@app.route('/events/page/<string:page>', methods=['GET'])
def events(page):
    return jsonify(events=get_events("events", page))

@app.route('/events/<string:id>', methods=['GET'])
def event(id):
    return jsonify(event=get_event(id))

@app.route('/days/<string:id>/events', methods=['GET'], defaults={'page': 1})
@app.route('/days/<string:id>/events/page/<int:page>', methods=['GET'])
def day_events(id, page):
    return jsonify(events=get_events("days:" + id + ":events", page))

@app.route('/miners/<string:id>/events', methods=['GET'], defaults={'page': 1})
@app.route('/miners/<string:id>/events/page/<int:page>', methods=['GET'])
def miner_events(id, page):
    return jsonify(events=get_events("miners:" + id + ":events", page))

@app.route('/days', methods=['GET'])
def days():
    days = r.smembers("days")
    return jsonify(days=list(days))

@app.route('/links', methods=['GET'])
def links():
    links_data = []
    links = r.smembers("links")
    for link in links:
        link_data = r.hgetall("links:" + str(link))
        link_data['id'] = link
        links_data.append(link_data)
    return jsonify(links=links_data)

@app.route('/links/<string:id>', methods=['GET'])
def link():
    link = r.hgetall("links:" + id)
    return jsonify(link=link)


@app.route('/chain/<string:head>', methods=['GET'])
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
    data['blocks'] = r.zcard("blocks")
    data['days'] = r.scard("days")
    data['events'] = r.zcard("events")
    return jsonify(summary=data)

@socketio.on('my event', namespace=SIMULATOR_NAMESPACE)
def test_message(message):
    emit('my response', {'data': message['data']})

@socketio.on('controls:start', namespace=SIMULATOR_NAMESPACE)
def start(message):
    emit('log', {'data': message}, broadcast=True)


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
