import itertools
from pathlib import Path

import numpy as np
import pandas as pd
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination
from pgmpy.models import BayesianNetwork

# Define the structure of the Bayesian network
# Node structure map: node -> list of parents
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

# Ordered list of nodes, ensuring roots are generally first for clarity
NODES = ["asia", "smoke", "tub", "lung", "bronc", "either", "xray", "dysp"]

# Corresponding (Parent, Child) edges for BayesianNetwork constructor
EDGES = []
for child, parents in STRUCTURE_MAP.items():
    for parent in parents:
        EDGES.append((parent, child))

# Mappings for data preprocessing and CPT state names
# Data will be mapped to 0 ('no') and 1 ('yes')
NUMERIC_STATE_MAP = {"no": 0, "yes": 1}
# For pgmpy state_names in CPDs and output readability (index 0='no', 1='yes')
STRING_STATES = ["no", "yes"]


def load_and_preprocess_data(file_path: Path) -> pd.DataFrame:
    """Loads data from CSV and maps 'yes'/'no' string values to integers 0/1."""
    df = pd.read_csv(file_path)
    for col in df.columns:
        if df[col].dtype == "object":  # Process columns with string data
            df[col] = df[col].str.lower().map(NUMERIC_STATE_MAP)
        elif pd.api.types.is_bool_dtype(df[col]):  # Handle boolean if present
            df[col] = df[col].astype(int)
    # After mapping, attempt to convert to integer type.
    # If mapping produced NaNs (e.g. from unexpected strings), this might error or create float cols.
    # It's crucial that columns become integer 0/1.
    for col in NODES:  # Check specifically our network nodes
        if col in df.columns and df[col].isnull().any():
            print(
                f"Warning: Column '{col}' contains NaN values after mapping. This may indicate unexpected values in CSV."
            )
            print(
                "Attempting to fill NaNs with a default (e.g., 0 or mode), or dropping rows might be needed."
            )
            # For now, we'll rely on subsequent checks to catch issues.
        # Attempt to convert to int, coercing errors to NaN then checking
        try:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype(
                "Int64"
            )  # Use Int64 to support Pandas NA
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
    child_card_numeric = len(STRING_STATES)  # Assumes 2 states: 0 and 1

    # State names for pgmpy TabularCPD for readability in output
    pgmpy_state_names = {child_node: STRING_STATES}
    if parent_nodes:
        for p_node in parent_nodes:
            pgmpy_state_names[p_node] = STRING_STATES

    if not parent_nodes:  # Root node
        probs = df[child_node].value_counts(normalize=True, dropna=False)
        ordered_probs = [probs.get(0, 0.0), probs.get(1, 0.0)]

        # Handle cases like all-NaN column or column with only one value after dropna in value_counts
        if sum(ordered_probs) == 0 and child_card_numeric > 0:
            ordered_probs = [1.0 / child_card_numeric] * child_card_numeric
        elif (
            abs(sum(ordered_probs) - 1.0) > 1e-9
        ):  # Normalize if sum is not 1 (e.g. due to only one value present)
            current_sum = sum(ordered_probs)
            if current_sum > 0:
                ordered_probs = [p / current_sum for p in ordered_probs]
            else:  # Should not happen if child_card_numeric > 0
                ordered_probs = [1.0 / child_card_numeric] * child_card_numeric

        cpt_values_list = [
            [p] for p in ordered_probs
        ]  # pgmpy expects [[P(state0)], [P(state1)], ...]
        cpt = TabularCPD(
            variable=child_node,
            variable_card=child_card_numeric,
            values=cpt_values_list,
            state_names=pgmpy_state_names,
        )
    else:  # Node with parents
        evidence_card_numeric = [child_card_numeric] * len(parent_nodes)

        num_parent_configs = np.prod(evidence_card_numeric)
        cpt_values_arr = np.zeros((child_card_numeric, num_parent_configs))

        parent_numeric_states_for_product = [list(range(child_card_numeric))] * len(
            parent_nodes
        )
        alpha = 1.0  # Laplace smoothing parameter

        for col_idx, parent_assignment_tuple in enumerate(
            itertools.product(*parent_numeric_states_for_product)
        ):
            query_parts = [
                f"`{parent_nodes[i]}` == {parent_assignment_tuple[i]}"
                for i in range(len(parent_nodes))
            ]
            query_str = " & ".join(query_parts)

            sub_df = (
                df.query(query_str) if query_str else df
            )  # df if no parents (though this branch is for parents)

            current_col_probs = []
            if (
                sub_df.empty or sub_df[child_node].isnull().all()
            ):  # No data or only NaNs for child for this config
                for _ in range(child_card_numeric):
                    current_col_probs.append(1.0 / child_card_numeric)  # Uniform
            else:
                # Drop NaNs for child node before value_counts for this specific sub_df
                counts = sub_df[child_node].dropna().value_counts()
                total_count_for_config = counts.sum()  # Sum of non-NaN counts

                if total_count_for_config == 0:  # All were NaN for child in this sub_df
                    for _ in range(child_card_numeric):
                        current_col_probs.append(1.0 / child_card_numeric)  # Uniform
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

    data_file_path = Path("raport") / "ASIA_DATA.csv"
    print(f"Attempting to load data from: {data_file_path.resolve()}")
    if not data_file_path.exists():
        print(f"ERROR: Data file not found at {data_file_path.resolve()}")
        print(
            "Please ensure ASIA_DATA.csv is in a 'raport' subdirectory relative to the script's execution location."
        )
        return

    df = load_and_preprocess_data(data_file_path)

    # Critical validation: Ensure all node columns are present and are 0 or 1.
    for node in NODES:
        if node not in df.columns:
            print(f"ERROR: Node column '{node}' is missing in the loaded data.")
            return
        # Check if column contains only 0 and 1 (or pd.NA if Int64)
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

    print("\\nBuilding Bayesian Network model...")
    model = BayesianNetwork(EDGES)

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

    print("\\nChecking model validity...")
    try:
        model.check_model()
        print("Model is valid.")
    except Exception as e:
        print(f"Model is INVALID: {e}")
        # Further debugging: print individual CPTs if model check fails
        # for c in cpds_list:
        #     print(c)
        return

    print("\\nCreating inference object (VariableElimination)...")
    infer = VariableElimination(model)

    print("\\n--- Task 2: Inference Queries ---")

    # 2a. Joint a priori distribution for all variables
    print("\\n2a. Joint a priori P(all variables):")
    try:
        joint_all_prior = infer.query(variables=NODES, joint=True)
        print("Full joint distribution for all 8 variables (2^8 = 256 states).")
        print("Displaying a part of the factor:")
        # Factor object can be large, str(factor) might be huge.
        # pgmpy's Factor.__str__ usually paginates for very large factors.
        print(joint_all_prior)
    except Exception as e:
        print(f"Error calculating joint a priori for all variables: {e}")

    # 2b. Joint a priori distribution for a selected subset of variables
    subset_vars_b = ["lung", "bronc", "xray"]
    print(f"\\n2b. Joint a priori P({', '.join(subset_vars_b)}):")
    try:
        joint_subset_prior = infer.query(variables=subset_vars_b, joint=True)
        print(joint_subset_prior)
    except Exception as e:
        print(f"Error calculating joint a priori for subset {subset_vars_b}: {e}")

    # 2c. Marginal a posteriori (conditional) for all variables except evidence
    evidence_c_numeric = {"asia": 1, "smoke": 0}  # asia='yes', smoke='no'
    evidence_c_str = {k: STRING_STATES[v] for k, v in evidence_c_numeric.items()}
    print(
        f"\\n2c. Marginal a posteriori distributions given evidence: {evidence_c_str}"
    )

    query_vars_c = [node for node in NODES if node not in evidence_c_numeric.keys()]

    for var_name in query_vars_c:
        try:
            marginal_posterior = infer.query(
                variables=[var_name], evidence=evidence_c_numeric
            )
            print(f"\\nP({var_name} | {evidence_c_str}):")
            print(marginal_posterior)
        except Exception as e:
            print(f"Error calculating P({var_name} | {evidence_c_str}): {e}")

    # 2d. Joint a posteriori (conditional) for selected variables except evidence
    subset_vars_d = ["tub", "either"]
    evidence_d_numeric = evidence_c_numeric
    evidence_d_str = evidence_c_str
    print(
        f"\\n2d. Joint a posteriori P({', '.join(subset_vars_d)} | {evidence_d_str}):"
    )
    try:
        joint_subset_posterior = infer.query(
            variables=subset_vars_d, evidence=evidence_d_numeric, joint=True
        )
        print(joint_subset_posterior)
    except Exception as e:
        print(
            f"Error calculating joint a posteriori for {subset_vars_d} | {evidence_d_str}: {e}"
        )

    print("\\n\\nScript finished.")


if __name__ == "__main__":
    main()
