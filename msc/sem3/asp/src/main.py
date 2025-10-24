import argparse
from datetime import datetime
from pathlib import Path

from data_loader import load_graph
from experiment1 import detect_bot_communities
from experiment2 import analyze_assortativity_and_core_periphery

OUTPUT_DIR = Path(__file__).parent.parent / "outputs"


def parse_args():
    parser = argparse.ArgumentParser(description="Bot detection experiments")
    parser.add_argument(
        "--experiment",
        type=str,
        default="all",
        choices=["all", "experiment1", "experiment2"],
        help="Experiment to run",
    )
    return parser.parse_args()


def main(experiment: str):
    """
    Main function to run the bot detection experiments.
    """
    # Create a unique output directory for this run
    run_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = OUTPUT_DIR / f"run_{run_timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"Results for this run will be saved in: {output_dir}")

    # Load the graph
    print("Loading graph data...")
    G = load_graph()
    print("Graph loaded successfully.")

    # Run Experiment 1
    if experiment == "all" or experiment == "experiment1":
        print("Running Experiment 1...")
        detect_bot_communities(G, output_dir)

    # Run Experiment 2
    if experiment == "all" or experiment == "experiment2":
        print("Running Experiment 2...")
        analyze_assortativity_and_core_periphery(G, output_dir)


if __name__ == "__main__":
    args = parse_args()
    main(args.experiment)
