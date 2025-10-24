from pathlib import Path

import networkx as nx
from visualize import (
    plot_bot_percentage_by_core,
    plot_degree_distribution,
    visualize_k_core,
)


def analyze_assortativity_and_core_periphery(G: nx.DiGraph, output_dir: Path):
    """
    Analyzes assortativity and core-periphery structure of the graph.

    Args:
        G (nx.DiGraph): The input graph with 'label' attributes on nodes.
        output_dir (Path): The directory to save the results.
    """
    report_lines = []
    print("\nExperiment 2: Analysis of Assortativity and Core-Periphery Structure")
    report_lines.append(
        "Experiment 2: Analysis of Assortativity and Core-Periphery Structure"
    )

    # Attribute assortativity for bot/human labels
    # Note: A node might not have a 'label' if it's not in the label.csv but is in edge.csv
    # We'll filter to nodes that have the label attribute.
    labeled_nodes = [n for n, d in G.nodes(data=True) if "label" in d]
    subgraph_labeled = G.subgraph(labeled_nodes)

    # The function below works only for integers, so lets map labels to 0 and 1
    # human -> 0, bot -> 1
    labels = {
        n: 1 if d["label"] == "bot" else 0 for n, d in subgraph_labeled.nodes(data=True)
    }
    nx.set_node_attributes(subgraph_labeled, labels, "label_code")

    attribute_assortativity = nx.attribute_assortativity_coefficient(
        subgraph_labeled, "label_code"
    )
    assortativity_str = (
        f"Attribute Assortativity (bot/human): {attribute_assortativity:.4f}"
    )
    print(assortativity_str)
    report_lines.append(assortativity_str)

    # Degree assortativity
    degree_assortativity = nx.degree_assortativity_coefficient(G)
    degree_assortativity_str = f"Degree Assortativity: {degree_assortativity:.4f}"
    print(degree_assortativity_str)
    report_lines.append(degree_assortativity_str)

    # K-core decomposition
    print("\nK-Core Decomposition Analysis:")
    report_lines.append("\nK-Core Decomposition Analysis:")
    # Create a copy of the graph to find cores, as it removes nodes
    core_G = G.copy()
    cores = nx.core_number(core_G)

    # Add core number as an attribute
    nx.set_node_attributes(G, cores, "core_number")

    max_core = max(cores.values()) if cores else 0
    max_core_str = f"Max core number: {max_core}"
    print(max_core_str)
    report_lines.append(max_core_str)

    core_analysis_results = []
    for k in range(max_core + 1):
        k_core_nodes = [n for n, core_num in cores.items() if core_num >= k]
        if not k_core_nodes:
            continue

        bots_in_core = len(
            [n for n in k_core_nodes if G.nodes[n].get("label") == "bot"]
        )
        humans_in_core = len(
            [n for n in k_core_nodes if G.nodes[n].get("label") == "human"]
        )
        total_in_core = bots_in_core + humans_in_core

        if total_in_core > 0:
            bot_percentage = (bots_in_core / total_in_core) * 100
            core_analysis_str = f"Core {k}: Total Nodes={total_in_core}, Bot Percentage={bot_percentage:.2f}%"
            print(core_analysis_str)
            report_lines.append(core_analysis_str)
            core_analysis_results.append(
                {
                    "core": k,
                    "total_nodes": total_in_core,
                    "bot_percentage": bot_percentage,
                }
            )

    # Save the full report
    experiment_output_dir = output_dir / "experiment2"
    experiment_output_dir.mkdir(parents=True, exist_ok=True)
    report_path = experiment_output_dir / "assortativity_and_core_analysis.txt"
    with open(report_path, "w") as f:
        f.write("\n".join(report_lines))
    print(f"\nAnalysis report saved to {report_path}")

    # Visualizations
    visualize_k_core(G, experiment_output_dir)
    plot_degree_distribution(G, experiment_output_dir)
    plot_bot_percentage_by_core(core_analysis_results, experiment_output_dir)


if __name__ == "__main__":
    from data_loader import load_graph

    # Create a dummy output dir for direct script run
    if not os.path.exists("outputs_test"):
        os.makedirs("outputs_test")

    graph = load_graph()
    analyze_assortativity_and_core_periphery(graph, "outputs_test")
