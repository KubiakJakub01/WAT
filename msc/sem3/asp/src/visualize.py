import networkx as nx
import matplotlib.pyplot as plt
import os
import pandas as pd
import numpy as np


def visualize_k_core(G, output_dir):
    """
    Visualizes the graph with node colors for labels and size for core number.

    Args:
        G (nx.DiGraph): The graph with 'label' and 'core_number' attributes.
        output_dir (str): The directory to save the visualization.
    """
    # Reduce the graph size for better visualization if it's too large
    if G.number_of_nodes() > 1000:
        print(
            "\nGraph is too large for direct visualization. Visualizing a subgraph of the main core."
        )
        max_core = max(nx.get_node_attributes(G, "core_number").values())
        core_nodes = [
            n for n, d in G.nodes(data=True) if d.get("core_number") == max_core
        ]
        H = G.subgraph(core_nodes)
    else:
        H = G

    pos = nx.spring_layout(H, iterations=50)

    # Node colors based on label
    node_colors = []
    for node in H.nodes():
        if H.nodes[node].get("label") == "bot":
            node_colors.append("red")
        elif H.nodes[node].get("label") == "human":
            node_colors.append("blue")
        else:
            node_colors.append("grey")  # For nodes without a label

    # Node sizes based on core number
    node_sizes = [d.get("core_number", 1) * 100 for n, d in H.nodes(data=True)]

    plt.figure(figsize=(15, 15))
    nx.draw(
        H,
        pos,
        node_color=node_colors,
        node_size=node_sizes,
        with_labels=False,
        width=0.5,
        alpha=0.7,
    )

    plt.title("Graph Visualization: Red=Bot, Blue=Human, Size=Core Number")
    # Save the plot to a file
    output_path = os.path.join(output_dir, "k_core_visualization.png")
    plt.savefig(output_path)
    print(f"\nVisualization saved to {output_path}")
    # plt.show() # Disabling interactive pop-up for batch runs


def plot_bot_contamination_by_community(community_results_df, output_dir, min_size=0):
    """
    Creates a bar chart of the bot contamination rate for the top N communities.

    Args:
        community_results_df (pd.DataFrame): DataFrame with community analysis.
        output_dir (str): The directory to save the plot.
        min_size (int): The minimum community size included in the data.
    """
    if community_results_df.empty:
        print("No communities with sufficient size to plot.")
        return

    # Sort by bot rate and take the top 20 for readability
    top_communities = community_results_df.sort_values(
        by="bot_rate", ascending=False
    ).head(20)

    plt.figure(figsize=(12, 8))
    plt.bar(
        top_communities["community_id"].astype(str),
        top_communities["bot_rate"],
        color="salmon",
    )
    plt.xlabel("Community ID")
    plt.ylabel("Bot Contamination Rate")
    plt.title(f"Top 20 Communities (Size >= {min_size}) by Bot Contamination Rate")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    output_path = os.path.join(output_dir, "bot_contamination_by_community.png")
    plt.savefig(output_path)
    print(f"Community contamination plot saved to {output_path}")
    # plt.show()


def plot_degree_distribution(G, output_dir):
    """
    Plots the degree distribution for bots and humans.

    Args:
        G (nx.DiGraph): The graph with 'label' attributes on nodes.
        output_dir (str): The directory to save the plot.
    """
    bots = [n for n, d in G.nodes(data=True) if d.get("label") == "bot"]
    humans = [n for n, d in G.nodes(data=True) if d.get("label") == "human"]

    bot_degrees = [G.degree(n) for n in bots]
    human_degrees = [G.degree(n) for n in humans]

    plt.figure(figsize=(12, 8))
    plt.hist(bot_degrees, bins=50, alpha=0.6, color="red", label="Bots", density=True)
    plt.hist(
        human_degrees, bins=50, alpha=0.6, color="blue", label="Humans", density=True
    )
    plt.xlabel("Degree")
    plt.ylabel("Probability Density")
    plt.title("Degree Distribution: Bots vs. Humans")
    plt.yscale("log")  # Use log scale for better visibility of tail
    plt.legend()
    plt.tight_layout()

    output_path = os.path.join(output_dir, "degree_distribution.png")
    plt.savefig(output_path)
    print(f"Degree distribution plot saved to {output_path}")
    # plt.show()


def plot_bot_percentage_by_core(core_analysis_data, output_dir):
    """
    Plots the percentage of bots in each k-core.

    Args:
        core_analysis_data (list): A list of dicts with core analysis data.
        output_dir (str): The directory to save the plot.
    """
    if not core_analysis_data:
        print("No core analysis data to plot.")
        return

    df = pd.DataFrame(core_analysis_data)

    plt.figure(figsize=(12, 8))
    plt.plot(
        df["core"], df["bot_percentage"], marker="o", linestyle="-", color="purple"
    )
    plt.xlabel("Core Number (k)")
    plt.ylabel("Percentage of Bots (%)")
    plt.title("Bot Percentage vs. Core Number")
    plt.grid(True)
    plt.tight_layout()

    output_path = os.path.join(output_dir, "bot_percentage_by_core.png")
    plt.savefig(output_path)
    print(f"Bot percentage by core plot saved to {output_path}")
    # plt.show()
