import networkx as nx

def draw_gamers(gamers, algo="sfdp"):
    pos = nx.nx_pydot.graphviz_layout(gamers, prog=algo)
    nx.draw_networkx(gamers, pos, node_size=25, width=.25,
                     node_color=list(nx.get_node_attributes(gamers, "max_sub_col").values()),
                     with_labels=False)


def random_test():
    G = nx.algorithms.bipartite.generators.gnmk_random_graph(100, 10, 125)
    nx.set_edge_attributes(G, "#FFB6C1", "color")

    nx.draw(G, nx.nx_pydot.graphviz_layout(G, "sfdp"), edge_color=nx.get_edge_attributes(G, "color").values())
