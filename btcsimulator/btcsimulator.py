__author__ = 'victor'

from redis import StrictRedis
from redis import ConnectionError
import numpy
import simpy
import hashlib
import pickle
from datetime import timedelta
import time

r = StrictRedis(host='localhost', port=6379, db=0)

def sha256(data):
    return hashlib.sha256(pickle.dumps(data)).hexdigest()

class Link:
    def __init__(self, origin, destination, delay):
        self.origin = origin
        self.destination = destination
        self.id = self.get_id()
        self.delay = delay
        # Store link in database
        self.store()

    def get_id(self):
        return RedisUtils.get_id("links")

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
        return RedisUtils.get_id("events")

    def store(self):
        key = "events:" + repr(self.id)
        # Store event
        data = {"destination": self.destination, "origin": self.origin, "action": self.action, "payload": self.payload, "time": self.time}
        if isinstance(self.payload, Block):
            data['payload'] = sha256(self.payload)
        r.hmset(key, data)
        day = TimeUtils.days_passed(self.time)
        r.zadd("events", self.time, self.id)
        r.zadd("days:" + repr(day) + ":events:" + repr(self.action), self.time, self.id)
        r.zadd("days:" + repr(day) + ":events", self.time, self.id)
        r.zadd("miners:" + repr(self.origin) + ":events", self.time, self.id)

class Block:
    def __init__(self, prev, height, time, miner_id, size, valid):
        self.prev = prev
        self.height = height
        self.time = time
        self.miner_id = miner_id
        self.size = size
        self.valid = valid
        # When a block is created it is stored in redis
        self.store()

    def store(self):
        key = 'blocks:' + str(sha256(self))
        # Store block in block list
        r.zadd("blocks", self.height, sha256(self))
        # Store the block info
        r.hmset(key, {'prev': self.prev, 'height':self.height, 'time': self.time, 'size': self.size, 'valid': self.valid, 'miner': self.miner_id})
        # Store reference block in the miner's blocks set
        r.zadd("miners:" + str(self.miner_id) + ":blocks-mined", self.height, sha256(self))

class Miner:

    # Define action names
    BLOCK_REQUEST = 1 # Hey! I need a block!
    BLOCK_RESPONSE = 2 # Here is the block you wanted!
    HEAD_NEW = 3 # I have a new chain head!
    BLOCK_NEW = 4 # Just mined a new block!
    ACK = 5 # ACK message with no data

    # Network block rate a.k.a 1 block every ten minutes
    BLOCK_RATE = 1.0 / 600.0
    # A miner is able to verify 200KBytes per seconds
    VERIFY_RATE = 200*1024

    def __init__(self, env, store, hashrate, verifyrate, seed_block):
        # Simulation environment
        self.env = env
        # Get miner id from redis
        self.id = self.get_id()
        # Socket
        self.socket = Socket(env, store, self.id)
        # Miner computing percentage of total network
        self.hashrate = hashrate
        # Miner block erification rate
        self.verifyrate = verifyrate
        # Store seed block
        self.seed_block = seed_block
        # Pointer to the block chain head
        self.chain_head = '*'
        # Hash with all the blocks the miner knows about
        self.blocks = dict()
        # Array with blocks needed to be processed
        self.blocks_new = []
        # Create event to notify when a block is mined
        self.block_mined = env.event()
        # Create event to notify when a new block arrives
        self.block_received = env.event()
        # Create event to notify when the mining process can continue
        self.continue_mining = env.event()
        self.mining = None
        # Store the miner in the database
        self.store()
        self.total_blocks = 0

    def get_id(self):
        return RedisUtils.get_id("miners")

    def store(self):
        key = "miners:" + str(self.id)
        r.hmset(key, {"hashrate": self.hashrate / Miner.BLOCK_RATE, "verifyrate": self.verifyrate})
        r.sadd("miners", self.id)


    def start(self):
        # Add the seed_block
        self.add_block(self.seed_block)
        # Start the process of adding blocks
        self.env.process(self.wait_for_new_block())
        # Receive network events
        self.env.process(self.receive_events())
        # Start mining and store the process so it can be interrupted
        self.mining = self.env.process(self.mine_block())

    def mine_block(self):
        # Indefinitely mine new blocks
        while True:
            try:
                # Determine block size
                block_size = 1024*200*numpy.random.random()
                # Determine the time the block will be mined depending on the miner hashrate
                time = numpy.random.exponential(1/self.hashrate, 1)[0]
                # Wait for the block to be mined
                yield self.env.timeout(time)
                # Once the block is mined it needs to be added. An event is triggered
                block = Block(self.chain_head, self.blocks[self.chain_head].height + 1, self.env.now, self.id, block_size, 1)
                self.notify_new_block(block)
            except simpy.Interrupt as i:
                # When the mining process is interrupted it cannot continue until it is told to continue
                yield self.continue_mining

    def notify_new_block(self, block):
        self.total_blocks += 1
        #print("%d \tI just mined a block at %7.4f" % (self.id, self.env.now))
        self.block_mined.succeed(block)
        # Create a new mining event
        self.block_mined = self.env.event()

    def notify_received_block(self, block):
        self.block_received.succeed(block)
        # Create a new block received event
        self.block_received = self.env.event()

    def stop_mining(self):
        self.mining.interrupt()

    def keep_mining(self):
        self.continue_mining.succeed()
        self.continue_mining = self.env.event()

    def add_block(self, block):
        # Add the seed block to the known blocks
        self.blocks[sha256(block)] = block
        # Store the block in redis
        r.zadd("miners:" + str(self.id) + ":blocks", block.height, sha256(block))
        # Announce block if chain_head isn't empty
        if self.chain_head == "*":
            self.chain_head = sha256(block)
        # If block height is greater than chain head, update chain head and announce new head
        if (block.height > self.blocks[self.chain_head].height):
            self.chain_head = sha256(block)
            self.announce_block(block)

    def wait_for_new_block(self):
        while True:
            # Wait for a block to be mined or received
            blocks = yield self.block_mined | self.block_received
            # Interrupt the mining process so the block can be added
            self.stop_mining()
            #print("%d \tI stop mining" % self.id)
            for event, block in blocks.items():
                #print("Miner %d - mined block at %7.4f" %(self.id, self.env.now))
                # Add the new block to the pending ones
                self.blocks_new.append(block)
                # Process new blocks
            yield self.env.process(self.process_new_blocks())
            # Keep mining
            self.keep_mining()

    def verify_block(self, block):
        # If block was mined by the miner but the previous block is not the chain head it will not be valid
        if block.miner_id == self.id and block.prev != self.chain_head:
            return -1
        # If the previous block is not in miner blocks it is not possible to validate current block
        if block.prev not in self.blocks:
            return 0
        # If block height isnt previous block + 1 it will not be valid
        if block.height != self.blocks[block.prev].height + 1:
            return -1
        return 1

    def process_new_blocks(self):
        blocks_later = []
        # Validate every new block
        for block in self.blocks_new:
            # Block validation takes some time
            yield self.env.timeout(block.size / self.verifyrate)
            valid = self.verify_block(block)
            if valid == 1:
                self.add_block(block)
            elif valid == 0:
                #Logger.log(self.env.now, self.id, "NEED_DATA", sha256(block))
                self.request_block(block.prev)
                blocks_later.append(block)
        self.blocks_new = blocks_later

    # Announce new head when block is added to the chain
    def announce_block(self, block):
        self.broadcast(Miner.HEAD_NEW, sha256(block))

    # Request a block to all links
    def request_block(self, block, to=None):
        #Logger.log(self.env.now, self.id, "REQUEST", block)
        if to is None:
            self.broadcast(Miner.BLOCK_REQUEST, block)
        else:
            self.send_event(to, Miner.BLOCK_REQUEST, block)

    # Send a block to a specific miner
    def send_block(self, block_hash, to):
        # Find the block
        block = self.blocks[block_hash]
        # Send the event
        self.send_event(to, Miner.BLOCK_RESPONSE, block)

    def send_ack(self, to):
        self.send_event(to, Miner.ACK, "")

    # Send certain event to a specific miner
    def send_event(self, to, action, payload):
        self.socket.send_event(to, action, payload)

    # Broadcast an event to all links
    def broadcast(self, action, payload):
        self.socket.broadcast(action, payload)

    def receive_events(self):
        while True:
            # Wait for a network event
            if len(self.socket.links) == 0:
                return
            data = yield self.socket.receive(self.id)
            if data.action == Miner.BLOCK_REQUEST:
                # Send block if we have it
                if data.payload in self.blocks:
                    self.send_block(data.payload, data.origin)
                # Otherwise send ACK
                else:
                    self.send_ack(data.origin)
            elif data.action == Miner.BLOCK_RESPONSE:
                self.notify_received_block(data.payload)
            elif data.action == Miner.HEAD_NEW:
                # If we don't have the new head, we need to request it
                if data.payload not in self.blocks:
                    self.request_block(data.payload)
                # Otherwise send ack
                else:
                    self.send_ack(data.origin)

            #print("Miner %d - receives block %d at %7.4f" %(self.id, sha256(data), self.env.now))

    def add_link(self, destination, delay):
        link = Link(self.id, destination, delay)
        self.socket.add_link(link)
        r.sadd("miners:" + str(self.id) + ":links", link.id)

    @staticmethod
    def connect(miner, other_miner):
        miner.add_link(other_miner.id, 0.02)
        other_miner.add_link(miner.id, 0.02)

class TimeUtils:

    @staticmethod
    def days_passed(seconds):
        return timedelta(seconds=seconds).days

    @staticmethod
    def get_seconds(days):
        return days*24*3600

class RedisUtils:

    @staticmethod
    def get_id(key):
        return r.incr("ids:" + key)

    @staticmethod
    def configure_event_names():
        r.sadd("events:types", Miner.BLOCK_REQUEST, Miner.BLOCK_RESPONSE, Miner.BLOCK_NEW, Miner.HEAD_NEW)

    @staticmethod
    def store_days(days):
        seq = range(0,days)
        for i in seq:
            r.sadd("days", i)

class Simulator:

    @staticmethod
    def mine():
        try:
            # Clear redis database before new simulation starts
            r.flushdb()
        except ConnectionError:
            return -1
        # Store in redis the simulation event names
        RedisUtils.configure_event_names()
        days = 1
        simulation_time = 50000 #TimeUtils.get_seconds(days)
        env = simpy.Environment()
        store = simpy.FilterStore(env)
        seed_block = Block(None, 0, env.now, -1, 0, 1)
        miners = []
        miners.append( Miner(env, store, 0.5068986167220384 * Miner.BLOCK_RATE, Miner.VERIFY_RATE, seed_block))
        miners.append(Miner(env, store, 0.085196940891858156 * Miner.BLOCK_RATE, Miner.VERIFY_RATE, seed_block))
        miners.append(Miner(env, store, 0.40790444238610346 * Miner.BLOCK_RATE, Miner.VERIFY_RATE, seed_block))
        Miner.connect(miners[0], miners[1])
        Miner.connect(miners[0], miners[2])
        Miner.connect(miners[1], miners[2])
        for miner in miners: miner.start()
        start = time.time()
        # Start simulation until limit. Time unit is seconds
        env.run(until=simulation_time)
        end = time.time()
        print("Simulation took: %1.4f seconds" % (end - start))
        # Store in redis simulation days
        RedisUtils.store_days(days)
        # After simulation store every miner head, so their chain can be built again
        for miner in miners: r.hset("miners:" + repr(miner.id), "head", miner.chain_head)
        # Notify simulation ended
        r.publish("/btcsimulator", "simulation ended")
        return 0


    @staticmethod
    def standard(miners_number=20, days=10):
        # Convert simulation days to seconds
        simulation_time = TimeUtils.get_seconds(days)
        try:
            # Clear redis database before new simulation starts
            r.flushdb()
        except ConnectionError:
            return -1
        # Store in redis the simulation event names
        RedisUtils.configure_event_names()
        # Create simpy environment
        env = simpy.Environment()
        store = simpy.FilterStore(env)
        # Create the seed block
        seed_block = Block(None, 0, env.now, -1, 0, 1)
        hashrates = numpy.random.dirichlet(numpy.ones(miners_number), size=1)
        # Create miners
        miners = []
        # This dict is used to store the connections between miners, so they are not created twice
        connections = dict()
        for i in range(0, miners_number):
            miner = Miner(env, store, hashrates[0,i] * Miner.BLOCK_RATE, Miner.VERIFY_RATE, seed_block)
            miners.append(miner)
            connections[miner] = dict()
        # Randomly connect miners
        for i, miner in enumerate(miners):
            miner_connections = numpy.random.choice([True, False], miners_number)
            for j, miner_connection in enumerate(miner_connections):
                # Onlye create connection if miner is not self and connection does not already exist
                if i != j and miner_connection == True and j not in connections[miner] and i not in connections[miners[j]]:
                    # Store connection so its not created twice
                    connections[miner][j] = True
                    connections[miners[j]][i] = True
                    Miner.connect(miner, miners[j])
        for miner in miners: miner.start()
        start = time.time()
        # Start simulation until limit. Time unit is seconds
        env.run(until=simulation_time)
        end = time.time()
        print("Simulation took: %1.4f seconds" % (end - start))
        # Store in redis simulation days
        RedisUtils.store_days(days)
        # After simulation store every miner head, so their chain can be built again
        for miner in miners: r.hset("miners:" + repr(miner.id), "head", miner.chain_head)
        # Notify simulation ended
        r.publish("/btcsimulator", "simulation ended")
        return 0

if __name__ == '__main__':
    Simulator.standard(6, 10)


