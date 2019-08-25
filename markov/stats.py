import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.cm as cm
import numpy as np
import mc
import better_graph
import copy


def get_absorbing_map(node_map, target_conf):
    length = len(node_map)
    winning_nodes = []
    nmap = copy.deepcopy(node_map)
    for key in node_map:
        if node_map[key].attack_blocks > target_conf:
            nmap[key].right = node_map[key].id
            nmap[key].left = node_map[key].id
            winning_nodes.append(copy.deepcopy(node_map[key]))
        elif node_map[key].honest_blocks == target_conf:
            if length not in node_map:
                nmap[length] = mc.Node(
                    len(node_map),
                    node_map[key].alpha,
                    node_map[key].beta,
                    None)
                nmap[length].set_prob(0.0)
                nmap[length].set_children(
                    length,
                    length)
            nmap[key].right = length

    return nmap, winning_nodes


def run():
    alpha = 0.3
    beta = 0.5
    # target confirmations
    for k in range(2, 8):
        node_map, winning_nodes = get_absorbing_map(mc.build_rect_graph(alpha, beta, k), k)
        for i in node_map:
            print(node_map[i])
        matrix = mc.markov_chain_gen(node_map)
        final = mc.start(matrix, k, alpha, beta)
        win_prob = 0.0
        print(final)
        for inx, elt in enumerate(winning_nodes):

            win_prob += final[0, elt.id]
        print(win_prob)


def run_split():
    # target confirmations
    plt.clf()
    num = 50
    xs = np.arange(2, num, 1)
    fig, ax = plt.subplots()
    for _, beta in enumerate([0.5, 0.6, 0.7]):
        alpha_values = [round(i, 2) for i in np.arange(0.1, beta, 0.1) if i + beta <= 1.0]
        for inx, alpha in enumerate(alpha_values):
            ys = []
            for k in range(2, num):
                node_map, final_nodes = better_graph.split_graph(alpha, beta, k)
                matrix = better_graph.markov_chain_gen(node_map)
                converge = np.linalg.matrix_power(matrix, k * 3)
                ys.append(converge[0][final_nodes[0]])
            ax.plot(xs, ys, label='α = {}, β = {}'.format(alpha, beta))
    ax.set_title('Success probability with varying power fractions')
    ax.set_xlabel('Number of confirmations')
    ax.set_ylabel('Probabilitiy of success')
    ax.set_xticks(np.arange(0, num, 10))
    ax.set_yticks(np.arange(0, 0.6, 0.1))
    plt.grid()
    plt.legend()
    plt.savefig('artifacts/split-graph.png'.format(beta))



if __name__ == '__main__':
    run_split()
