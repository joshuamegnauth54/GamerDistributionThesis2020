import networkx as nx

# Maybe put these in a notebook?
# gamers_df.groupby("author").subreddit.nunique().sort_values(ascending=False)

def deg_cent_metrics(gamers_df, projection):
    """Return a sorted degree centrality dict so I don't have to keep typing
    the line below."""
    dc = sorted(nx.degree_centrality(projection).items(),
                key=lambda x: x[1])
    return dc

def sorted_components(projection):
    return sorted(nx.connected_components(projection), key=len, reverse=True)

def largest_connected_component(projection):
    return nx.subgraph(projection,
                       sorted_components(projection)[0])


