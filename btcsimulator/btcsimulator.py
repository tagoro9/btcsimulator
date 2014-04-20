__author__ = 'victor'

from redis import StrictRedis
import numpy
import simpy
import random
import collections

r = StrictRedis(host='localhost', port=6379, db=0)

class Cable:
    def __init__(self, env, delay):
        self.env = env
        self.delay = delay
        self.store = simpy.Store(env)

    def latency(self, value):
        yield self.env.timeout(self.delay)
        self.store.put(value)

    def put(self, value):
        self.env.process(self.latency(value))

    def get(self):
        return self.store.get()

class Link:
    def __init__(self, destination, send_cable, receive_cable):
        self.destination = destination
        self.send_cable = send_cable
        self.receive_cable = receive_cable
        self.id = self.get_id()
        # Store link in database
        self.store()

    def get_id(self):
        return r.incr("ids:links")

    def store(self):
        key = "links:" + str(self.id)
        r.hmset(key, {"destination": self.destination, "delay": self.send_cable.delay})

    def send(self, value):
        self.send_cable.put(value)

    def receive(self):
        return self.receive_cable.get()


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
        key = 'blocks:' + str(hash(self))
        # Store the block info
        r.hmset(key, {'prev': self.prev, 'height':self.height, 'time': self.time, 'size': self.size, 'valid': self.valid})
        # Store reference block in the miner's blocks set
        r.sadd("miners:" + str(self.miner_id) + ":blocks", hash(self))

class Miner:
    def __init__(self, env, hashrate, seed_block):
        # Simulation environment
        self.env = env
        # Get miner id from redis
        self.id = self.get_id()
        # Miner computing percentage of total network
        self.hashrate = hashrate
        # Pointer to the block chain head
        self.chain_head = '*'
        # Hash with all the blocks the miner knows about
        self.blocks = dict()
        # Array with blocks needed to be processed
        self.blocks_new = []
        # Create event to notify when a block is mined
        self.block_mined = env.event()
        # Create event to notify when the mining process can continue
        self.continue_mining = env.event()
        # Array with links to other nodes
        self.link = None
        self.mining = None
        # Store the miner in the database
        self.store()

    def get_id(self):
        return r.incr("ids:miners")


    def store(self):
        key = "miners:" + str(self.id)
        r.hmset(key, {"hashrate": self.hashrate})
        r.sadd("miners", self.id)


    def start(self):
        # Add the seed_block
        self.add_block(seed_block)
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
        self.block_mined.succeed(block)
        # Create a new mining event
        self.block_mined = env.event()

    def stop_mining(self):
        self.mining.interrupt()

    def keep_mining(self):
        self.continue_mining.succeed()
        self.continue_mining = env.event()

    def add_block(self, block):
        # Add the seed block to the known blocks
        self.blocks[hash(block)] = block
        # Announce block if chain_head isn't empty
        if self.chain_head != "*":
            self.announce_block(block)
        # Update the chain head
        self.chain_head = hash(block)

    def wait_for_new_block(self):
        while True:
            # Wait for a block to be mined
            block = yield self.block_mined
            #print("Miner %d - mined block at %7.4f" %(self.id, self.env.now))
            # Interrupt the mining process so the block can be added
            self.stop_mining()
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
        # Block validation takes some time
        yield self.env.timeout(10)
        # Validate every new block
        for block in self.blocks_new:
            valid = self.verify_block(block)
            if valid == 1:
                self.add_block(block)
        self.blocks_new = []

    def announce_block(self, block):
        #print("Miner %d - announce block %d at %7.4f" % (self.id, hash(block), self.env.now))
        self.link.send(block)

    def receive_events(self):
        while True:
            data = yield self.link.receive()
            #print("Miner %d - receives block %d at %7.4f" %(self.id, hash(data), self.env.now))

    def add_link(self, destination, send, receive):
        self.link = Link(destination, send, receive)
        r.sadd("miners:" + str(self.id) + ":links", self.link.id)


# Clear redis database before new simulation starts
r.flushdb()

env = simpy.Environment()
seed_block = Block(None, 0, env.now, -1, 0, 1)
miner1 = Miner(env, 0.3, seed_block)
miner2 = Miner(env, 0.7, seed_block)
cable1 = Cable(env, 2)
cable2 = Cable(env,2)
miner1.add_link(miner2.id, cable1, cable2)
miner2.add_link(miner1.id, cable2, cable1)

miner1.start()
miner2.start()

env.run(until=100)





