import itertools
from pathlib import Path

import numpy as np
import pandas as pd
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination
from pgmpy.models import DiscreteBayesianNetwork

STRUCTURE_MAP = {
    "asia": [],
    "smoke": [],
    "tub": ["asia"],
    "lung": ["smoke"],
    "bronc": ["smoke"],
    "either": ["tub", "lung"],
    "xray": ["either"],
    "dysp": ["bronc", "either"],
}

NODES = ["asia", "smoke", "tub", "lung", "bronc", "either", "xray", "dysp"]

EDGES = []
for child, parents in STRUCTURE_MAP.items():
    for parent in parents:
        EDGES.append((parent, child))

NUMERIC_STATE_MAP = {"no": 0, "yes": 1}
STRING_STATES = ["no", "yes"]


def load_and_preprocess_data(file_path: Path) -> pd.DataFrame:
    """Loads data from CSV and maps 'yes'/'no' string values to integers 0/1."""
    df = pd.read_csv(file_path)
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].str.lower().map(NUMERIC_STATE_MAP)
        elif pd.api.types.is_bool_dtype(df[col]):
            df[col] = df[col].astype(int)
    for col in NODES:
        if col in df.columns and df[col].isnull().any():
            print(
                f"Warning: Column '{col}' contains NaN values after mapping. This may indicate unexpected values in CSV."
            )
            print(
                "Attempting to fill NaNs with a default (e.g., 0 or mode), or dropping rows might be needed."
            )
        try:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
        except Exception as e:
            print(f"Could not convert column {col} to numeric: {e}")

    return df


def create_cpt(
    df: pd.DataFrame, child_node: str, parent_nodes: list[str]
) -> TabularCPD:
    """
    Creates a TabularCPD for the child_node given its parents,
    learning probabilities from the dataframe.
    Uses Laplace smoothing (alpha=1) for observed parent configurations.
    Uses uniform distribution for unobserved parent configurations.
    All nodes are assumed to be binary with states 0 ('no') and 1 ('yes').
    """
    child_card_numeric = len(STRING_STATES)

    pgmpy_state_names = {child_node: STRING_STATES}
    if parent_nodes:
        for p_node in parent_nodes:
            pgmpy_state_names[p_node] = STRING_STATES

    if not parent_nodes:
        probs = df[child_node].value_counts(normalize=True, dropna=False)
        ordered_probs = [probs.get(0, 0.0), probs.get(1, 0.0)]

        if sum(ordered_probs) == 0 and child_card_numeric > 0:
            ordered_probs = [1.0 / child_card_numeric] * child_card_numeric
        elif abs(sum(ordered_probs) - 1.0) > 1e-9:
            current_sum = sum(ordered_probs)
            if current_sum > 0:
                ordered_probs = [p / current_sum for p in ordered_probs]
            else:
                ordered_probs = [1.0 / child_card_numeric] * child_card_numeric

        cpt_values_list = [[p] for p in ordered_probs]
        cpt = TabularCPD(
            variable=child_node,
            variable_card=child_card_numeric,
            values=cpt_values_list,
            state_names=pgmpy_state_names,
        )
    else:
        evidence_card_numeric = [child_card_numeric] * len(parent_nodes)

        num_parent_configs = np.prod(evidence_card_numeric)
        cpt_values_arr = np.zeros((child_card_numeric, num_parent_configs))

        parent_numeric_states_for_product = [list(range(child_card_numeric))] * len(
            parent_nodes
        )
        alpha = 1.0

        for col_idx, parent_assignment_tuple in enumerate(
            itertools.product(*parent_numeric_states_for_product)
        ):
            query_parts = [
                f"`{parent_nodes[i]}` == {parent_assignment_tuple[i]}"
                for i in range(len(parent_nodes))
            ]
            query_str = " & ".join(query_parts)

            sub_df = df.query(query_str) if query_str else df

            current_col_probs = []
            if sub_df.empty or sub_df[child_node].isnull().all():
                for _ in range(child_card_numeric):
                    current_col_probs.append(1.0 / child_card_numeric)
            else:
                counts = sub_df[child_node].dropna().value_counts()
                total_count_for_config = counts.sum()

                if total_count_for_config == 0:
                    for _ in range(child_card_numeric):
                        current_col_probs.append(1.0 / child_card_numeric)
                else:
                    for child_state_val_numeric in range(child_card_numeric):
                        prob = (counts.get(child_state_val_numeric, 0) + alpha) / (
                            total_count_for_config + alpha * child_card_numeric
                        )
                        current_col_probs.append(prob)

            cpt_values_arr[:, col_idx] = current_col_probs

        cpt = TabularCPD(
            variable=child_node,
            variable_card=child_card_numeric,
            values=cpt_values_arr.tolist(),
            evidence=parent_nodes,
            evidence_card=evidence_card_numeric,
            state_names=pgmpy_state_names,
        )
    return cpt


def main():
    """Main function to build the Bayesian network and perform inference."""
    print("Starting Bayesian Network construction and inference for 'Asia' dataset.\\n")

    data_file_path = Path(__file__).parent / "raport" / "ASIA_DATA.csv"
    print(f"Attempting to load data from: {data_file_path.resolve()}")
    if not data_file_path.exists():
        print(f"ERROR: Data file not found at {data_file_path.resolve()}")
        print(
            "Please ensure ASIA_DATA.csv is in a 'raport' subdirectory relative to the script's execution location."
        )
        return

    df = load_and_preprocess_data(data_file_path)

    for node in NODES:
        if node not in df.columns:
            print(f"ERROR: Node column '{node}' is missing in the loaded data.")
            return
        valid_values = df[node].dropna().isin([0, 1])
        if not valid_values.all():
            print(
                f"ERROR: Column '{node}' contains values other than 0 or 1 after preprocessing."
            )
            print(f"Unique non-NaN values in '{node}': {df[node].dropna().unique()}")
            return
        if df[node].isnull().any():
            print(
                f"ERROR: Column '{node}' still contains NaN values after preprocessing. This will cause issues in CPT calculation."
            )
            print("Please clean the data so all nodes have 0 or 1 values.")
            return

    print("\nBuilding Bayesian Network model...")
    model = DiscreteBayesianNetwork(EDGES)

    cpds_list = []
    print("Estimating CPTs from data...")
    for node_name in NODES:
        parents = STRUCTURE_MAP[node_name]
        print(
            f"  Creating CPT for '{node_name}' with parents {parents if parents else '[]'}"
        )
        cpt = create_cpt(df, node_name, parents)
        cpds_list.append(cpt)

    model.add_cpds(*cpds_list)

    print("\nChecking model validity...")
    try:
        model.check_model()
        print("Model is valid.")
    except Exception as e:
        print(f"Model is INVALID: {e}")
        return

    print("\nCreating inference object (VariableElimination)...")
    infer = VariableElimination(model)

    print("\n--- Task 2: Inference Queries ---")

    # 2a. Joint a priori distribution for all variables
    print("\n2a. Joint a priori P(all variables):")
    try:
        joint_all_prior = infer.query(variables=NODES, joint=True)
        print("Full joint distribution for all 8 variables (2^8 = 256 states).")
        print("Displaying a part of the factor:")
        output_path = Path(__file__).parent / "raport" / "joint_distribution.txt"
        with open(output_path, "w") as f:
            f.write(str(joint_all_prior))
        print(f"\nJoint distribution saved to {output_path}")
    except Exception as e:
        print(f"Error calculating joint a priori for all variables: {e}")

    # 2b. Joint a priori distribution for a selected subset of variables
    subset_vars_b = ["lung", "bronc", "xray"]
    print(f"\n2b. Joint a priori P({', '.join(subset_vars_b)}):")
    try:
        joint_subset_prior = infer.query(variables=subset_vars_b, joint=True)
        print(joint_subset_prior)
    except Exception as e:
        print(f"Error calculating joint a priori for subset {subset_vars_b}: {e}")

    # 2c. Marginal a posteriori (conditional) for all variables except evidence
    evidence_c_numeric = {"asia": 1, "smoke": 0}  # asia='yes', smoke='no'
    evidence_c_str = {k: STRING_STATES[v] for k, v in evidence_c_numeric.items()}
    print(f"\n2c. Marginal a posteriori distributions given evidence: {evidence_c_str}")

    query_vars_c = [node for node in NODES if node not in evidence_c_numeric.keys()]

    for var_name in query_vars_c:
        try:
            marginal_posterior = infer.query(
                variables=[var_name], evidence=evidence_c_str
            )
            print(f"\nP({var_name} | {evidence_c_str}):")
            print(marginal_posterior)
        except Exception as e:
            print(f"Error calculating P({var_name} | {evidence_c_str}): {e}")

    # 2d. Joint a posteriori (conditional) for selected variables except evidence
    subset_vars_d = ["tub", "either"]
    evidence_d_str = evidence_c_str
    print(f"\n2d. Joint a posteriori P({', '.join(subset_vars_d)} | {evidence_d_str}):")
    try:
        joint_subset_posterior = infer.query(
            variables=subset_vars_d, evidence=evidence_d_str, joint=True
        )
        print(joint_subset_posterior)
    except Exception as e:
        print(
            f"Error calculating joint a posteriori for {subset_vars_d} | {evidence_d_str}: {e}"
        )

    print("\n\nScript finished.")


if __name__ == "__main__":
    main()
