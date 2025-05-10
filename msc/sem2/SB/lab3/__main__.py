import pprint

import numpy as np
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination
from pgmpy.models import DiscreteBayesianNetwork

# Step 1: Create the network structure
abc_model = DiscreteBayesianNetwork([("A", "B"), ("A", "C")])

cpd_a = TabularCPD(variable="A", variable_card=2, values=[[0.4], [0.6]])
cpd_b = TabularCPD(
    variable="B",
    variable_card=2,
    evidence=["A"],
    evidence_card=[2],
    values=[
        [0.2, 0.6],  # P(WD=złe | D, JD)
        [0.8, 0.4],  # P(WD=dobre | D, JD)
    ],
)

cpd_c = TabularCPD(
    variable="C",
    variable_card=2,
    evidence=["A"],
    evidence_card=[2],
    values=[
        [0.8, 0.3],  # P(WD=złe | D, JD)
        [0.2, 0.7],  # P(WD=dobre | D, JD)
    ],
)
# Step 3: Add CPDs to the model
abc_model.add_cpds(cpd_a, cpd_b, cpd_c)

# Step 4: Check if the model is correctly defined
assert abc_model.check_model()

abc_infer = VariableElimination(abc_model)

a = abc_infer.query(variables=["A"])
print(a)
b = abc_infer.query(variables=["B"])
print(b)
c = abc_infer.query(variables=["C"])
print(c)

joint_distribution_abc = abc_infer.query(variables=["A", "B", "C"])
print(joint_distribution_abc)

joint_distribution_bc = abc_infer.query(variables=["B", "C"])
print(joint_distribution_bc)

cond_ab_given_c_zero = abc_infer.query(variables=["A", "B"], evidence={"C": 0})
print(cond_ab_given_c_zero)

cond_bc_given_a_one = abc_infer.query(variables=["B", "C"], evidence={"A": 1})
print(cond_bc_given_a_one)

# Verify conditional independence of B and C given A using d-separation
is_dependent = abc_model.is_dconnected("B", "C", observed=["A"])
print(f"Are B and C conditionally independent given A? {not is_dependent}")

# --- Verification using NumPy based on distributions ---

# P(A, B, C)
p_abc = joint_distribution_abc.values

# P(A)
p_a = a.values

# Calculate P(B, C | A) = P(A, B, C) / P(A)
# Add new axes to p_a for broadcasting: (2,) -> (2, 1, 1)
p_bc_given_a = p_abc / p_a[:, np.newaxis, np.newaxis]

# Calculate P(B | A) by marginalizing P(B, C | A) over C
# Sum over axis 2 (C)
p_b_given_a = np.sum(p_bc_given_a, axis=2)

# Calculate P(C | A) by marginalizing P(B, C | A) over B
# Sum over axis 1 (B)
p_c_given_a = np.sum(p_bc_given_a, axis=1)

# Calculate the product P(B | A) * P(C | A)
# Add new axes for broadcasting: (2, 2) -> (2, 2, 1) and (2, 2) -> (2, 1, 2)
product = p_b_given_a[:, :, np.newaxis] * p_c_given_a[:, np.newaxis, :]

# Check if P(B, C | A) == P(B | A) * P(C | A)
are_independent_numpy = np.allclose(p_bc_given_a, product)

print(f"P(B, C | A):\n{p_bc_given_a}")
print(f"P(B | A) * P(C | A):\n{product}")
print(f"Are B and C conditionally independent given A (NumPy check)? {are_independent_numpy}")
