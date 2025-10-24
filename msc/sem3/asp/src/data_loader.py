from pathlib import Path

import networkx as nx
import pandas as pd
from tqdm import tqdm

DATA_PATH = Path(__file__).parent.parent / "data" / "twibot"


def load_graph():
    edges_df = pd.read_csv(DATA_PATH / "edge.csv")
    labels_df = pd.read_csv(DATA_PATH / "label.csv")

    # Create a directed graph
    G = nx.DiGraph()

    # Add nodes with labels
    for _, row in tqdm(labels_df.iterrows(), total=len(labels_df), desc="Adding nodes"):
        G.add_node(row["id"], label=row["label"])

    # Add edges for 'following' and 'followers'
    for _, row in tqdm(edges_df.iterrows(), total=len(edges_df), desc="Adding edges"):
        if row["relation"] in ["following", "followers"]:
            G.add_edge(row["source_id"], row["target_id"], relation=row["relation"])

    return G


if __name__ == "__main__":
    # Example of how to load the graph
    graph = load_graph()
    print(
        f"Graph loaded with {graph.number_of_nodes()} nodes and {graph.number_of_edges()} edges."
    )
    # print some node attributes
    for node in list(graph.nodes(data=True))[:5]:
        print(node)
