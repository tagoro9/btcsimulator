import moment
from persistence import *
from block import Block, sha256


class Link:
    def __init__(self, origin, destination, delay):
        self.origin = origin
        self.destination = destination
        self.id = self.get_id()
        self.delay = delay
        # Store link in database
        self.store()

    def get_id(self):
        return get_id("links")

    def store(self):
        key = "links:" + str(self.id)
        r.sadd("links", self.id)
        r.hmset(key, {"destination": self.destination, "delay": self.delay, 'origin': self.origin})

    def send(self, value):
        self.socket.send(value, self.delay)


class Socket:
    def __init__(self, env, store, miner_id):
        self.miner_id = miner_id
        self.store = store
        self.env = env
        self.links = dict()

    def add_link(self, link):
        self.links[link.destination] = link

    def send(self, value, delay):
        self.env.process(self.process_send(value, delay))

    def process_send(self, value, delay):
        yield self.env.timeout(delay)
        self.store.put(value)

    # Send certain event to a specific miner
    def send_event(self, to, action, payload):
        event = Event(to, self.miner_id, self.env.now, action, payload)
        self.send(event, self.links[to].delay)

    # Broadcast an event to all links
    def broadcast(self, action, payload):
        for to in self.links:
            event = Event(to, self.miner_id, self.env.now, action, payload)
            self.send(event, self.links[to].delay)

    def receive(self, miner_id):
        return self.store.get(filter=lambda event: event.destination == miner_id)

class Event:
    def __init__(self, destination, origin, time, action, payload):
        self.destination = destination
        self.origin = origin
        self.action = action
        self.payload = payload
        self.time = time
        self.id = self.get_id()
        self.store()

    def get_id(self):
        return get_id("events")

    def store(self):
        key = "events:" + repr(self.id)
        # Store event
        data = {"destination": self.destination, "origin": self.origin, "action": self.action, "payload": self.payload, "time": self.time}
        if isinstance(self.payload, Block):
            data['payload'] = sha256(self.payload)
        r.hmset(key, data)
        day = moment.days_passed(self.time)
        r.zadd("events", self.time, self.id)
        r.zadd("days:" + repr(day) + ":events:" + repr(self.action), self.time, self.id)
        r.zadd("days:" + repr(day) + ":events", self.time, self.id)
        r.zadd("miners:" + repr(self.origin) + ":events", self.time, self.id)