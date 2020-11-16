import networkx as nx
import matplotlib.pyplot as plt

def draw_gamers(gamers, algo="sfdp", color="sub_color", edge_color="#282a36",
                size=32):
    pos = nx.nx_pydot.graphviz_layout(gamers, prog=algo)
    fig, ax = plt.subplots(figsize=(16, 16))
    nx.draw_networkx(gamers,
                     pos,
                     with_labels=False,
                     ax=ax,
                     node_size=size,
                     node_color=list(nx.get_node_attributes(gamers, color).values()),
                    # alpha=0.75,
                     edge_color=list(nx.get_node_attributes(gamers, edge_color).values()),
                     label=color
                     )
    fig.tight_layout()
    fig.patch.set_facecolor("#282a36")
    ax.patch.set_facecolor("#282a36")
    return (fig, ax)

def draw_degree_centrality(gamers):
    deg_cent = [dc * 10000 for dc in nx.degree_centrality(gamers).values()]
    return draw_gamers(gamers, color="SysGamGen", edge_color="sub_color",
                       size=deg_cent)
