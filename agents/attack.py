from util import BlockType
from agents.agent import Agent

MAX_INT = 99999999999999999999999999.999


class AttackAgent(Agent):
    """
    AttackAgent
    """
    def __init__(self, block_rate, k_conf, network):
        super().__init__(block_rate, BlockType.InvalidBlock, 'attack', network)
        self.k = k_conf
        self.unvalidated_spends = 0

    def try_add_block(self, block):
        self.resolve_fork([block])

    def resolve_fork(self, blocks, agent_decisions):
        # get max height block
        index, max_ht_block = max(
            enumerate(blocks),
            key=lambda e: e[1].height)

        if max_ht_block.height <= self.chain_tip.height:
            return

        # get all max height blocks
        max_ht_blocks = list(filter(
            lambda e: e.height == max_ht_block.height,
            blocks)
        )
        # sort max height blocks by time, ascending
        min_time_blocks = sorted(max_ht_blocks, key=lambda e: e.time)
        # count number of invalid blocks in chain before accepting
        # next valid block (i.e. when SPV miner switches to valid chain)
        if not self.chain_tip.is_valid and min_time_blocks[0].is_valid:
            temp = self.chain_tip
            inx = 0
            while not temp.is_valid:
                temp = temp.parent
                inx += 1

            if inx > self.k:
                self.unvalidated_spends += 1

        self.add_block(min_time_blocks[0])
        return
