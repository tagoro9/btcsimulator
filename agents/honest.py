from util import BlockType
from agents.agent import Agent

MAX_INT = 99999999999999999999999999.999


class HonestAgent(Agent):
    """
    HonestAgent
    """
    def __init__(self, block_rate, network):
        super().__init__(block_rate, BlockType.FullBlock, 'honest', network)

    def is_valid_chain(self, block):
        temp = block
        while temp.height > 0:
            if temp.is_valid:
                temp = temp.parent
            else:
                return False
        return True

    def try_add_block(self, block):
        self.resolve_fork([block])

    def resolve_fork(self, blocks):
        leftover_blocks = blocks
        # honest agent processes blocks by max height
        # and min time and discards invalid blocks.
        while len(leftover_blocks) > 0:
            # get max height block
            index, max_ht_block = max(
                enumerate(leftover_blocks),
                key=lambda e: e[1].height)
            if max_ht_block.height < self.chain_tip.height:
                break
            # get all max height blocks
            max_ht_blocks = list(filter(
                lambda e: e.height == max_ht_block.height,
                leftover_blocks)
            )
            # get rest of blocks
            leftover_blocks = list(filter(
                lambda e: not e.height == max_ht_block.height and e.height,
                leftover_blocks)
            )
            # sort max height blocks by time, ascending
            min_time_blocks = sorted(max_ht_blocks, key=lambda e: e.time)

            while len(min_time_blocks) > 0:
                elt = min_time_blocks.pop(0)
                if elt.identifier == 'attack':
                    continue
                elif elt.identifier == 'spv':
                    if self.is_valid_chain(elt):
                        self.add_block(elt)
                        return
                    else:
                        continue
                else:
                    # add honest block
                    self.add_block(elt)
                    return
