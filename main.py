from persistence import *
from block import Block
from miner import Miner, BadMiner, SelfishMiner
import moment
import simpy
import time
import numpy


class Simulator:

    SIMULATION_ENDED = "SIMULATION_ENDED"
    PUBSUB_CHANNEL = "/btcsimulator"

    @staticmethod
    def standard(miners_number=20, days=10):
        # Convert simulation days to seconds
        simulation_time = moment.get_seconds(days)
        try:
            clear_db()
        except ConnectionError:
            return -1
        # Store in redis the simulation event names
        configure_event_names([Miner.BLOCK_REQUEST, Miner.BLOCK_RESPONSE, Miner.BLOCK_NEW, Miner.HEAD_NEW])
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
        store_days(days)
        # After simulation store every miner head, so their chain can be built again
        for miner in miners: r.hset("miners:" + repr(miner.id), "head", miner.chain_head)
        # Notify simulation ended
        r.publish(Simulator.PUBSUB_CHANNEL, Simulator.SIMULATION_ENDED)
        return 0


if __name__ == '__main__':
    Simulator.standard(3, 1)
