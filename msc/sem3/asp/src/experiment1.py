import os
from pathlib import Path

import networkx as nx
import pandas as pd
from community import community_louvain
from visualize import plot_bot_contamination_by_community

MIN_COMMUNITY_SIZE = 3


def detect_bot_communities(G: nx.DiGraph, output_dir: Path):
    """
    Detects and analyzes communities to find "bot nests".

    Args:
        G (nx.DiGraph): The input graph with 'label' attributes on nodes.
        output_dir (Path): The directory to save the results.
    """
    # For Louvain algorithm, we need an undirected graph
    undirected_G = G.to_undirected()

    # Detect communities using the Louvain algorithm
    partition = community_louvain.best_partition(undirected_G)

    # Create a dictionary to hold communities
    communities = {}
    for node, community_id in partition.items():
        if community_id not in communities:
            communities[community_id] = []
        communities[community_id].append(node)

    # Calculate bot contamination rate for each community
    bot_contamination_rates = {}
    for cid, members in communities.items():
        bots = [
            node
            for node in members
            if "label" in G.nodes[node] and G.nodes[node]["label"] == "bot"
        ]
        if len(members) > 0:
            bot_contamination_rates[cid] = len(bots) / len(members)

    # Calculate the average bot rate for the entire graph
    total_bots = len([n for n, d in G.nodes(data=True) if d.get("label") == "bot"])
    average_bot_rate = (
        total_bots / G.number_of_nodes() if G.number_of_nodes() > 0 else 0
    )

    print("Experiment 1: Community Detection and Analysis of 'Bot Nests'")
    print(f"Average bot contamination rate across the graph: {average_bot_rate:.2%}")
    print("-" * 30)

    # Prepare data for saving
    community_results = []

    # Identify communities with a higher percentage of bots than average
    for cid, rate in sorted(
        bot_contamination_rates.items(), key=lambda item: item[1], reverse=True
    ):
        if rate > average_bot_rate:
            community_size = len(communities[cid])
            print(f"Community {cid}: Size={community_size}, Bot Rate={rate:.2%}")
            community_results.append(
                {"community_id": cid, "size": community_size, "bot_rate": rate}
            )

    # Save results to a CSV file
    experiment_output_dir = output_dir / "experiment1"
    experiment_output_dir.mkdir(parents=True, exist_ok=True)
    results_df = pd.DataFrame(community_results)

    # Filter for communities with a minimum size to focus on significant clusters
    filtered_df = results_df[results_df["size"] >= MIN_COMMUNITY_SIZE].copy()

    output_path = experiment_output_dir / "bot_contamination_by_community.csv"
    filtered_df.to_csv(output_path, index=False)
    print(
        f"\nBot contamination by community results (size >= {MIN_COMMUNITY_SIZE}) saved to {output_path}"
    )

    # Generate and save the visualization
    plot_bot_contamination_by_community(
        filtered_df, experiment_output_dir, MIN_COMMUNITY_SIZE
    )


if __name__ == "__main__":
    from data_loader import load_graph

    # Create a dummy output dir for direct script run
    if not os.path.exists("outputs_test"):
        os.makedirs("outputs_test")

    graph = load_graph()
    detect_bot_communities(graph, "outputs_test")
