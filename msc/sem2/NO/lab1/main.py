import math
import os

import numpy as np
import pandas as pd


def read_data(file_path):
    # Construct path relative to the script file
    script_dir = os.path.dirname(__file__)
    absolute_path = os.path.join(script_dir, file_path)
    print(f"Attempting to read data from: {absolute_path}")  # Debug print
    data = pd.read_csv(absolute_path, sep="\t", header=None)
    # Flatten the data frame to a single array
    times = data.values.flatten()
    return times


def calculate_rhs(times, N):
    """
    Calculates the Right Hand Side (RHS) of the derived MLE equation.
    RHS = 2n / (T * N - sum(j * times[j]^2)) for j=0 to n-1
    """
    n = len(times)
    if n == 0:
        return None

    T = np.sum(times**2)
    if T == 0:
        print("Error in RHS: Sum of squares of times (T) is zero.")
        return None  # Or handle as appropriate, maybe NaN

    sum_j_tj_squared = np.sum(np.arange(n) * (times**2))

    denominator = T * N - sum_j_tj_squared
    if abs(denominator) < 1e-15:  # Check for near-zero denominator
        print("Error in RHS: Denominator is zero or very close to zero.")
        # Return NaN or raise an error
        return np.nan

    rhs_value = (2.0 * n) / denominator
    return rhs_value


def schick_wolverton_mle(times, precision=1e-11):
    """
    Implement the Schick-Wolverton model MLE calculation per the formulas.
    Uses iterative refinement for N and Phi.
    Formulas:
    T = sum(t_i^2) for i=1 to n
    Phi = (2 / T) * sum(1 / (N - (i-1))) for i=1 to n
    N = (2n / (Phi * T)) + sum((i-1)^2 * t_i) / T for i=1 to n
    """
    n = len(times)
    if n == 0:
        return None, None

    # Pre-calculate sums that don't depend on N or Phi
    # Note: Formula indices i are 1 to n, Python indices j are 0 to n-1.
    # T = sum(t_j^2) for j=0 to n-1
    T = np.sum(times**2)
    print(f"T: {T}")
    if T == 0:
        print("Warning: Sum of squares of times (T) is zero.")
        return None, None  # Avoid division by zero

    # Calculate sum((i-1) * t_i^2) for i=1 to n
    # Corrected calculation: sum(j * times[j]^2) for j=0 to n-1
    sum_term_for_N = 0
    for j in range(n):
        # The formula is sum((i-1) * t_i^2), so in Python indices j=i-1: sum(j * times[j]^2)
        sum_term_for_N += j * (times[j] ** 2)

    N = float(2 * n)
    phi = 0.0

    max_iter = 2000  # Increased max iterations slightly
    for iteration in range(max_iter):
        # Store old N for convergence check
        N_old = N

        # Calculate sum(1 / (N - (i-1))) for i=1 to n
        # Equivalent to sum(1 / (N - j)) for j=0 to n-1
        sum_1_div_N_minus_j = 0
        needs_restart = False  # Flag to indicate if N was reset
        for j in range(n):
            denominator = N - j
            if denominator <= 0:
                # This N is invalid because N must be > n-1 for the sum term
                print(
                    f"Iteration {iteration}: N={N:.5f} is <= n-1 ({n - 1}). Resetting N."
                )
                # Reset N to a value slightly larger than n-1 to attempt recovery
                N = float(n)  # Reset N to be just > n-1
                needs_restart = True
                break  # Exit inner loop to restart the outer loop iteration
            sum_1_div_N_minus_j += 1.0 / denominator

        if needs_restart:
            continue  # Skip the rest of this iteration and restart with the new N

        # Calculate Phi using the formula: Phi = (2 / T) * sum_1_div_N_minus_j
        phi = (2.0 / T) * sum_1_div_N_minus_j

        # Check for invalid phi (e.g., if T was zero, though checked earlier)
        if phi <= 0 or (phi * T) == 0:
            print(
                f"Iteration {iteration}: Invalid intermediate value phi={phi:.10f}, T={T}. Stopping."
            )
            return None, None  # Cannot proceed

        # Calculate new N using the formula: N = (2n / (Phi * T)) + sum_term_for_N / T
        # Use the corrected sum term here
        new_N = (2.0 * n / (phi * T)) + (sum_term_for_N / T)
        print(f"{new_N=}")
        # Ensure N remains > n-1 for the next iteration's sum calculation
        if new_N <= n - 1:
            print(
                f"Iteration {iteration}: Calculated new_N={new_N:.5f} <= n-1 ({n - 1}). Adjusting N."
            )
            # Set N slightly above n-1 to allow the sum next iteration
            N = float(n) + 1
        else:
            N = new_N

        # Check convergence
        rhs = calculate_rhs(times, N)
        print(f"Rhs: {rhs}")
        print(f"Phi: {phi}")
        diff = rhs - phi
        print(f"Diff: {phi}")
        if abs(rhs - phi) < precision:
            # Converged, calculate final phi for the converged N
            sum_1_div_N_minus_j = 0
            for j in range(n):
                # Should be safe now since N converged to a value > n-1
                if N - j <= 0:
                    print(f"Error: Converged N={N} is not > n-1={n - 1}. Check logic.")
                    return None, None
                sum_1_div_N_minus_j += 1.0 / (N - j)
            phi = (2.0 / T) * sum_1_div_N_minus_j
            print(
                f"Converged after {iteration + 1} iterations with N={N:.4f} and phi={phi:.10f}"
            )
            return N, phi

    print(f"Warning: MLE estimation did not converge after {max_iter} iterations.")
    return N, phi


def calculate_E_Tk(N, phi, k):
    """
    Calculates the expected time until the k-th bug discovery using the formula:
    E[T_k] = sqrt(pi / (2 * Phi * (N - (k-1))))
    Assumes k=197 based on the task description.
    """
    target_k_minus_1 = k - 1  # Corresponds to 196 for k=197

    if phi is None or N is None:
        print("Cannot calculate expected time: N or Phi is None.")
        return None
    if N <= target_k_minus_1:
        print(
            f"Cannot calculate E[T_{k}]: Estimated N ({N:.4f}) <= {target_k_minus_1}."
        )
        return None
    if phi <= 0:
        print(f"Cannot calculate E[T_{k}]: Estimated Phi ({phi:.10f}) <= 0.")
        return None

    denominator = 2 * phi * (N - target_k_minus_1)
    if denominator <= 0:
        print(f"Cannot calculate E[T_{k}]: Denominator (2*phi*(N-k+1)) is <= 0.")
        return None

    expected_time = math.sqrt(math.pi / denominator)
    return expected_time


if __name__ == "__main__":
    # Read time intervals from the file (now relative to script location)
    times = read_data("dane.tsv")
    n_data_points = len(times)
    print(f"Number of data points (n): {n_data_points}")

    if n_data_points > 0:
        # Find MLE estimators using the corrected Schick-Wolverton model
        N_mle, phi_mle = schick_wolverton_mle(times)

        if N_mle is not None and phi_mle is not None:
            print(f"MLE estimator for N: {N_mle:.4f}")
            print(f"MLE estimator for phi: {phi_mle:.10f}")

            # Calculate expected time to 197th bug using the correct formula
            target_bug_index = 197
            expected_time = calculate_E_Tk(N_mle, phi_mle, target_bug_index)

            if expected_time is not None:
                print(
                    f"Expected time until the {target_bug_index}th bug (E[T_{target_bug_index}]): {expected_time:.4f}"
                )
            else:
                # Message already printed by calculate_E_Tk
                pass
        else:
            print("MLE estimation failed.")
    else:
        print("No data points found in dane.tsv.")
