from util import BlockType
from agents.agent import Agent


MAX_INT = 99999999999999999999999999.999


class SPVAgent(Agent):
    """
    SPVAgent

    The SPVAgent always choses among the longest
    chains. If there are ties for longest chains,
    the SPVAgent chooses the one it receives the
    earliest.
    """
    def __init__(self, block_rate, network, val_time=0.0):
        super().__init__(block_rate, BlockType.EmptyBlock, 'spv', network)

    def try_add_block(self, block):
        self.resolve_fork([block])

    def resolve_fork(self, blocks):
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
        self.add_block(min_time_blocks[0])
