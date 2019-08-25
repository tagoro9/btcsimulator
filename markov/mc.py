import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.cm as cm
import numpy as np


class Node(object):
    def __init__(self, _id, alpha, beta, level, from_honest=False):
        super(Node, self).__init__()
        self.id = _id
        self.alpha = alpha
        self.beta = beta
        self.level = level
        self.left = None
        self.right = None
        self.left_prob = 0.0
        self.right_prob = 0.0
        self.attack_blocks = None
        self.honest_blocks = None
        self.from_honest = from_honest

    def set_children(self, left, right):
        self.left = left
        self.right = right

    def set_state(self, attack_blocks, honest_blocks):
        self.attack_blocks = attack_blocks
        self.honest_blocks = honest_blocks

    def set_prob(self, left_prob):
        self.left_prob = left_prob
        self.right_prob = 1 - left_prob

    def __str__(self):
        return "Node [ id: {}, level: {}, left: {}, right: {}, state: ({}, {}), prob: ({}, {}) ]".format(
            self.id,
            self.level,
            self.left,
            self.right,
            self.attack_blocks,
            self.honest_blocks,
            self.left_prob,
            self.right_prob)


def create_node_map(alpha, beta, conf):
    node_map = {}
    ctr = 0
    for i in range(2 * conf + 1):
        for j in range(i+1):
            node_map[ctr] = Node(ctr, alpha, beta, i)
            ctr += 1
    return node_map


def build_symmetric_graph(alpha, beta, target_conf):
    level_ct = 2 * target_conf + 1
    num_nodes = (level_ct * (level_ct + 1)) / 2
    node_map = create_node_map(alpha, beta, target_conf)
    been_in_queue = {0: True, 1: True, 2: True}
    # setup root node children
    root = node_map[0]
    root.set_children(1, 2)
    root.set_state(0, 0)
    # setup level 1 children state
    node_map[1].set_state(1, 0)
    node_map[2].set_state(0, 1)
    queue = [node_map[1], node_map[2]]
    # start counter at first no root child
    ctr = 3
    last_level = 1
    while len(queue) > 0:
        node = queue.pop(0)
        # if we drop down another level, increment counter again
        if node.level > last_level:
            ctr += 1
            last_level = node.level

        if ctr >= num_nodes:
            return node_map

        node.set_children(ctr, ctr + 1)
        if ctr not in been_in_queue:
            queue.append(node_map[ctr])
            node_map[ctr].set_state(node.attack_blocks + 1, node.honest_blocks)
            # set probabilities based on two chain states
            if node.attack_blocks + 1 >= node.honest_blocks:
                node_map[ctr].set_prob(1 - beta)
            else:
                node_map[ctr].set_prob(alpha)

            been_in_queue[ctr] = True
        if ctr + 1 not in been_in_queue and ctr + 1 < num_nodes:
            queue.append(node_map[ctr + 1])
            node_map[ctr + 1].set_state(node.attack_blocks, node.honest_blocks + 1)
            # set probabilities based on two chain states
            if node.attack_blocks >= node.honest_blocks + 1:
                node_map[ctr].set_prob(1 - beta)
            else:
                node_map[ctr].set_prob(alpha)
            been_in_queue[ctr + 1] = True

        ctr += 1

        if ctr >= num_nodes:
            return node_map


def build_rect_graph(alpha, beta, target_conf):
    num_nodes = ((target_conf + 1) * (target_conf + 2))
    print("Number of nodes: {}".format(num_nodes))
    node_map = {}
    been_in_queue = {0: True}
    root = Node(0, alpha, beta, 0)
    ctr = 1
    queue = [root]
    root.set_state(0, 0)
    last_level = 1
    print("Target conf: {}".format(target_conf))
    while len(queue) > 0:
        node = queue.pop(0)
        l_child = None
        r_child = None

        if node.level == 0:
            root.set_children(ctr, ctr + 1)
            root.set_prob(alpha)
            l_child = Node(ctr, alpha, beta, node.level + 1)
            l_child.set_state(node.attack_blocks + 1, node.honest_blocks)
            r_child = Node(ctr + 1, alpha, beta, node.level + 1)
            r_child.set_state(node.attack_blocks, node.honest_blocks + 1)
            queue.append(l_child)
            queue.append(r_child)
            ctr += 2
        else:
            if node.attack_blocks > target_conf:
                node.set_children(None, None)
                node.set_prob(0.0)
                if ctr not in been_in_queue:
                    r_child = Node(ctr, alpha, beta, node.level + 1)
                    r_child.set_state(node.attack_blocks, node.honest_blocks + 1)
                    r_child.set_children(None, 0)
                    r_child.set_prob(0.0)
                    queue.append(r_child)
                    been_in_queue[ctr] = True
            elif node.honest_blocks == target_conf:
                node.set_children(ctr, 0)
                node.set_prob(alpha)
                if ctr not in been_in_queue:
                    l_child = Node(ctr, alpha, beta, node.level + 1)
                    l_child.set_state(node.attack_blocks + 1, node.honest_blocks)
                    queue.append(l_child)
                    been_in_queue[ctr] = True
                ctr += 1
            else:
                node.set_children(ctr, ctr + 1)
                if ctr not in been_in_queue:
                    l_child = Node(ctr, alpha, beta, node.level + 1)
                    l_child.set_state(node.attack_blocks + 1, node.honest_blocks)
                    queue.append(l_child)
                    if node.attack_blocks + 1 >= node.honest_blocks:
                        node.set_prob(1 - beta)
                    else:
                        node.set_prob(alpha)

                    been_in_queue[ctr] = True


                if ctr + 1 not in been_in_queue:
                    r_child = Node(ctr + 1, alpha, beta, node.level + 1)
                    r_child.set_state(node.attack_blocks, node.honest_blocks + 1)
                    queue.append(r_child)
                    if node.attack_blocks >= node.honest_blocks + 1:
                        node.set_prob(1 - beta)
                    else:
                        node.set_prob(alpha)
                    been_in_queue[ctr + 1] = True
                ctr += 1

            if node.attack_blocks == 0 and node.honest_blocks < target_conf:
                ctr += 1

        node_map[node.id] = node
        if l_child:
            node_map[l_child.id] = l_child
        if r_child:
            node_map[r_child.id] = r_child

        if ctr >= num_nodes:
            return node_map


def print_queue(queue):
    for _, elt in enumerate(queue):
        print("In queue: {}".format(elt))


def markov_chain_gen(node_map):
    matrix = np.zeros([len(node_map), len(node_map)])
    for inx in node_map:
        node = node_map[inx]
        if node.left is not None and node.right is not None:
            matrix[node.id][node.left] = node.left_prob + matrix[node.id][node.left]
            matrix[node.id][node.right] = node.right_prob + matrix[node.id][node.right]
        else:
            matrix[node_map[inx].id][0] = 1.0
    return matrix


def stead_state_solver(matrix):
    left_eig = np.linalg.eig(matrix.transpose())
    return left_eig


def plot_prob_matrix(ax, m):
    XB = np.linspace(-1, 1, 28)
    YB = np.linspace(-1, 1, 28)
    X, Y = np.meshgrid(XB, YB)
    return ax.imshow(m, interpolation='none', cmap=plt.cm.jet)


def start(matrix, k, alpha, beta, title="reg"):
    fig = plt.figure()
    ax = fig.subplots()
    ax.set_title('Converge animation w/ alpha: {}, beta: {}, gamma: {}'.format(alpha, beta, 1 - alpha - beta), fontsize=12)
    img = []
    final = matrix
    for i in range(1, 100):
        final = np.linalg.matrix_power(matrix, i)
        img.append((plot_prob_matrix(ax, final),))
    anim = animation.ArtistAnimation(fig, img, interval=50, repeat_delay=3000,
                                   blit=True)
    anim.save('{}-converge-{}.mp4'.format(title, k), writer='imagemagick', fps=30)
    return final


if __name__ == '__main__':
    alpha = 0.3
    beta = 0.5
    # target confirmations

    # Set up formatting for the movie files
    Writer = animation.writers['ffmpeg']
    writer = Writer(fps=15, metadata=dict(artist='Me'), bitrate=1800)

    for k in range(3, 7):
        node_map = build_rect_graph(alpha, beta, k)
        for i in node_map:
            print(node_map[i])
        matrix = markov_chain_gen(node_map)
        start(matrix, k, alpha, beta)
