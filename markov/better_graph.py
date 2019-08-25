import numpy as np


WIN_STATE = [-1, 0]
LOSE_STATE = [0, -1]


class SimpleNode(object):
    """docstring for SimpleNode"""
    def __init__(self, _id, state, from_honest):
        super(SimpleNode, self).__init__()
        self.id = _id
        self.state = state
        self.from_honest = from_honest
        self.prob = None
        self.children = None
        self.swap_state = False

    def set_prob(self, prob):
        self.prob = [prob, 1 - prob]

    def set_left_child(self, left):
        if self.children is not None:
            self.children[0] = left
        else:
            self.children = [left, None]

    def set_right_child(self, right):
        if self.children is not None:
            self.children[1] = right
        else:
            self.children = [None, right]

    def set_children(self, children):
        self.children = children

    def __str__(self):
        return "Node {} - ({}, {}, {}), prob: ({}), children: ({})".format(
            self.id,
            self.state[0],
            self.state[1],
            self.from_honest,
            self.prob,
            self.children)


def split_graph(alpha, beta, target_conf):
    nmap = {}
    seen = {}
    final_nodes = []
    root = SimpleNode(0, [0, 0], True)
    queue = [root]
    nmap[0] = root
    ctr = 1
    while len(queue) > 0:
        node = queue.pop(0)
        if node.state[0] > target_conf or node.state == WIN_STATE or node.state == LOSE_STATE:
            if node.state == WIN_STATE or node.state == LOSE_STATE:
                node.set_prob(0.0)
                node.set_children([node.id, node.id])
                final_nodes.append(node.id)
            continue

        from_honest = node.from_honest
        if node.state[0] > node.state[1]:
            node.set_prob(1 - beta)
            from_honest = False
        elif node.state[0] < node.state[1]:
            node.set_prob(alpha)
            from_honest = True
        else:
            if node.from_honest:
                node.set_prob(alpha)
            else:
                node.set_prob(1 - beta)

        left_unique = True
        right_unique = True
        if node.state[0] + 1 == node.state[1]:
            left_unique = False
        if node.state[1] + 1 == node.state[0]:
            right_unique = False

        left_state = [node.state[0] + 1, node.state[1]]
        right_state = [node.state[0], node.state[1] + 1]

        if node.state[0] + 1 > target_conf:
            left_state = WIN_STATE
        if node.state[1] + 1 > target_conf:
            right_state = LOSE_STATE

        node.set_children([ctr, ctr + 1])
        left_lookup = (left_state[0], left_state[1])
        right_lookup = (right_state[0], right_state[1])
        if left_lookup not in seen or left_state[0] == left_state[1]:
            node.set_left_child(ctr)
            nmap[ctr] = SimpleNode(
                ctr,
                left_state,
                from_honest)
            seen[left_lookup] = ctr
            queue.append(nmap[ctr])
            ctr += 1
        else:
            node.set_left_child(seen[left_lookup])

        if right_lookup not in seen or right_state[0] == right_state[1]:
            node.set_right_child(ctr)
            nmap[ctr] = SimpleNode(
                ctr,
                right_state,
                from_honest)
            seen[right_lookup] = ctr
            queue.append(nmap[ctr])
            ctr += 1
        else:
            node.set_right_child(seen[right_lookup])

    return nmap, final_nodes


def split_with_error(alpha, beta, target_conf):
    nmap = {}
    seen = {}
    final_nodes = []
    root = SimpleNode(0, [0, 0], True)
    queue = [root]
    nmap[0] = root
    ctr = 1
    while len(queue) > 0:
        node = queue.pop(0)
        if node.state[0] > target_conf or node.state == WIN_STATE or node.state == LOSE_STATE:
            if node.state == WIN_STATE or node.state == LOSE_STATE:
                node.set_prob(0.0)
                node.set_children([node.id, node.id])
                final_nodes.append(node.id)
            continue

        from_honest = node.from_honest
        # set node probability
        if node.state[0] > node.state[1]:
            node.set_prob(1 - beta)
            from_honest = False
        elif node.state[0] < node.state[1]:
            node.set_prob(alpha)
            from_honest = True
        else:
            if node.from_honest:
                node.set_prob(alpha)
            else:
                node.set_prob(1 - beta)


    return nmap, final_nodes


def markov_chain_gen(node_map):
    matrix = np.zeros([len(node_map), len(node_map)])
    for inx in node_map:
        node = node_map[inx]
        matrix[node.id][node.children[0]] = node.prob[0] + matrix[node.id][node.children[0]]
        matrix[node.id][node.children[1]] = node.prob[1] + matrix[node.id][node.children[1]]
    return matrix
