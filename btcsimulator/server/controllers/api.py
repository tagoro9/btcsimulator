__author__ = 'victor'

from . import app
from ..core import r, crossdomain, logger
from ..tasks import start_simulation_task
from flask import jsonify, request
from zato.redis_paginator import ZSetPaginator


def get_block(id):
    block_data = r.hgetall("blocks:" + id)
    block_data['hash'] = id
    return block_data


def get_event(id):
    event_data = r.hgetall("events:" + id)
    event_data['id'] = id
    # if event_data['action'] == str(Miner.BLOCK_REQUEST):
    #     event_data['action'] = "BLOCK_REQUEST"
    # elif event_data['action'] == str(Miner.BLOCK_RESPONSE):
    #     event_data['action'] = "BLOCK_RESPONSE"
    # elif event_data['action'] == str(Miner.BLOCK_NEW):
    #     event_data['action'] = "BLOCK_NEW"
    # elif event_data['action'] == str(Miner.HEAD_NEW):
    #     event_data['action'] = "HEAD_NEW"
    # elif event_data['action'] == str(Miner.ACK):
    #     event_data['action'] = "ACK"
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

@app.route('/miners', methods=['GET'])
@crossdomain(origin='*')
def miners():
    miners = r.smembers("miners")
    minersData = []
    for miner in miners:
        minersData.append(get_miner(miner))
    return jsonify(data=minersData)

def get_miner_links(id):
    data = []
    links = r.smembers("miners:" + id + ":links")
    for link in links:
        link_data = r.hgetall("links:" + link)
        data.append(link_data)
    return data

def get_miner(id):
    data = r.hgetall("miners:" + id)
    data['id'] = id
    data['blocks_mined'] = r.zcard("miners:" + id + ":blocks-mined")
    data['blocks'] = r.zcard("miners:" + id + ":blocks")
    data['links'] = get_miner_links(id)
    return data

@app.route('/miners/<string:id>', methods=['GET'])
@crossdomain(origin='*')
def miner(id):
    return jsonify(data=get_miner(id))

@app.route('/miners/<string:id>/links', methods=['GET'])
@crossdomain(origin='*')
def miner_links(id):
    return jsonify(data=get_miner_links(id))

@app.route('/miners/<string:id>/blocks', methods=['GET'], defaults={'page': 1})
@app.route('/miners/<string:id>/blocks/page/<int:page>')
@crossdomain(origin='*')
def miner_blocks(id, page):
    return jsonify(data=get_blocks("miners:" + id + ":blocks", page))

@app.route('/miners/<string:id>/blocks-mined', methods=['GET'], defaults={'page': 1})
@app.route('/miners/<string:id>/blocks-mined/page/<int:page>', methods=['GET'])
@crossdomain(origin='*')
def miner_blocks_mined(id, page):
    return jsonify(data=get_blocks("miners:" + id + ":blocks-mined", page))

@app.route('/blocks', methods=['GET'], defaults={'page': 1})
@app.route('/blocks/page/<page>', methods=['GET'])
@crossdomain(origin='*')
def blocks(page):
    return jsonify(data=get_blocks("blocks", page))

@app.route('/blocks/<string:id>', methods=['GET'])
@crossdomain(origin='*')
def block(id):
    block = r.hgetall("blocks:" + id)
    block['hash'] = id
    return jsonify(data=block)

@app.route('/events', methods=['GET'], defaults={'page': 1})
@app.route('/events/page/<string:page>', methods=['GET'])
@crossdomain(origin='*')
def events(page):
    return jsonify(data=get_events("events", page))

@app.route('/events/<string:id>', methods=['GET'])
@crossdomain(origin='*')
def event(id):
    return jsonify(data=get_event(id))

@app.route('/days/<string:id>/events', methods=['GET'], defaults={'page': 1})
@app.route('/days/<string:id>/events/page/<int:page>', methods=['GET'])
@crossdomain(origin='*')
def day_events(id, page):
    return jsonify(data=get_events("days:" + id + ":events", page))

@app.route('/miners/<string:id>/events', methods=['GET'], defaults={'page': 1})
@app.route('/miners/<string:id>/events/page/<int:page>', methods=['GET'])
@crossdomain(origin='*')
def miner_events(id, page):
    return jsonify(data=get_events("miners:" + id + ":events", page))

@app.route('/days', methods=['GET'])
@crossdomain(origin='*')
def days():
    days = r.smembers("days")
    return jsonify(data=list(days))

@app.route('/links', methods=['GET'])
@crossdomain(origin='*')
def links():
    links_data = []
    links = r.smembers("links")
    for link in links:
        link_data = r.hgetall("links:" + str(link))
        link_data['id'] = link
        links_data.append(link_data)
    return jsonify(data=links_data)

@app.route('/links/<string:id>', methods=['GET'])
@crossdomain(origin='*')
def link():
    link = r.hgetall("links:" + id)
    return jsonify(data=link)

# We just return first 10 blocks. Since it is a linked list it
# is quite easy to get the next page
@app.route('/chain/<string:head>', methods=['GET'])
@crossdomain(origin='*')
def chain(head):
    data = []
    count = 0
    while head != None and count < 100:
        block = get_block(head)
        if block['hash'] != "None":
            data.append(block)
        prev = r.hget("blocks:" + head, "prev")
        head = prev
        if head is None:
            a = 1
        count += 1
    return jsonify(data=data)

@app.route('/summary')
@crossdomain(origin='*')
def summary():
    data = dict()
    data['miners'] = r.scard("miners")
    data['links'] = r.scard("links")
    data['blocks'] = r.zcard("blocks")
    data['days'] = r.scard("days")
    data['events'] = r.zcard("events")
    return jsonify(data=data)


@app.route('/simulation', methods=['OPTIONS'])
@crossdomain(origin="*", headers=['Content-Type', 'Content-Disposition'])
def start_simulation_options():
    return None

@app.route('/simulation', methods=['POST'])
@crossdomain(origin="*", headers=['Content-Type', 'Content-Disposition'])
def start_simulation():
    simulation = request.json
    logger.info("Starting %d days %s simulation with %d miners" %(simulation['days'], simulation['type'], simulation['miners']))
    # Start the simulation in the worker
    start_simulation_task.delay(simulation['miners'], simulation['days'], simulation['type'])
    # Return simulation parameters
    return jsonify(request.json)