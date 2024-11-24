import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def parse_args():
    parser = argparse.ArgumentParser(description="Fourier Interpolation")
    parser.add_argument(
        "--min_n", type=int, default=40, help="Number of nodes for interpolation"
    )
    parser.add_argument(
        "--max_n", type=int, default=90, help="Number of nodes for interpolation"
    )
    parser.add_argument(
        "--window_size",
        type=int,
        default=5,
        help="Window size for calculating the quality",
    )
    parser.add_argument(
        "--plot_fp",
        type=Path,
        default="outputs/zad1/plot.png",
        help="Path to the output plot file",
    )
    parser.add_argument(
        "--output_fp",
        type=Path,
        default="outputs/zad1/output.txt",
        help="Path to the output file",
    )
    return parser.parse_args()


def r(theta):
    """Function r(theta) that we want to interpolate.

    Args:
        theta (float): Angle in radians.

    Returns:
        float: Value of the function r(theta) at the given
    """
    if 0 <= theta < np.pi / 2 or 3 * np.pi / 2 <= theta < 2 * np.pi:
        return 1.0
    elif np.pi / 2 <= theta < 3 * np.pi / 2:
        return 2.0


def generate_nodes(n):
    """Generate n nodes for interpolation.

    Args:
        n (int): Number of nodes.

    Returns:
        tuple: Tuple containing theta values and corresponding r(theta) values.
    """
    theta = np.linspace(0, 2 * np.pi, n, endpoint=False)
    values = np.array([r(t) for t in theta])
    return theta, values


def compute_fourier_coefficients(n, values):
    """Compute Fourier coefficients for the given values.

    Args:
        n (int): Number of nodes.
        values (np.array): Array of r(theta) values.

    Returns:
        tuple: Tuple containing a0, aj and bj coefficients.
    """
    m = n // 2 if n % 2 == 0 else (n - 1) // 2
    a0 = np.sum(values) / n
    aj = np.zeros(m)
    bj = np.zeros(m)

    for j in range(1, m + 1):
        aj[j - 1] = (2 / n) * np.sum(
            values * np.cos(j * np.linspace(0, 2 * np.pi, n, endpoint=False))
        )
        bj[j - 1] = (2 / n) * np.sum(
            values * np.sin(j * np.linspace(0, 2 * np.pi, n, endpoint=False))
        )

    return a0, aj, bj


def fourier_interpolation(n, a0, aj, bj, theta):
    """Compute the value of the Fourier interpolation polynomial at the given theta.

    Args:
        n (int): Number of nodes.
        a0 (float): Coefficient a0.
        aj (np.array): Array of aj coefficients.
        bj (np.array): Array of bj coefficients.
        theta (float): Angle in radians.

    Returns:
        float: Value of the Fourier interpolation polynomial at the given theta.
    """
    m = len(aj)

    if n % 2 == 0:
        result = (
            a0
            + sum(
                aj[j] * np.cos((j + 1) * theta) + bj[j] * np.sin((j + 1) * theta)
                for j in range(m)
            )
            + aj[m - 1] * np.cos(m * theta)
        )
    else:
        result = a0 + sum(
            aj[j] * np.cos((j + 1) * theta) + bj[j] * np.sin((j + 1) * theta)
            for j in range(m)
        )
    return result


def quality(theta_vals, interp_vals, window_size):
    """Calculate the quality of the interpolation.

    Args:
        theta_vals (np.array): Array of theta values.
        interp_vals (np.array): Array of interpolated values.

    Returns:
        float: Quality of the interpolation.
    """
    theta1 = np.pi / 2
    theta2 = 3 * np.pi / 2
    idx1 = np.argmin(np.abs(theta_vals - theta1))
    idx2 = np.argmin(np.abs(theta_vals - theta2))

    window_size = 5
    segment1 = np.array(
        interp_vals[
            max(0, idx1 - window_size) : min(len(theta_vals), idx1 + window_size)
        ]
    )
    segment2 = np.array(
        interp_vals[
            max(0, idx2 - window_size) : min(len(theta_vals), idx2 + window_size)
        ]
    )

    return max(
        np.max(np.abs(segment1 - r(theta1))), np.max(np.abs(segment2 - r(theta2)))
    )


def plot_interpolation(fine_theta, interpolated_vals, optimal_n, output_fp):
    """Plot the interpolation.

    Args:
        theta_vals (np.array): Array of theta values.
        interp_vals (np.array): Array of interpolated values.
        output_fp (Path): Path to the output plot file.
    """
    fig, ax = plt.subplots(subplot_kw={"projection": "polar"}, figsize=(8, 8))
    ax.plot(fine_theta, interpolated_vals, label="Fourier Interpolation", color="blue")
    ax.scatter(
        np.linspace(0, 2 * np.pi, optimal_n, endpoint=False),
        [r(t) for t in np.linspace(0, 2 * np.pi, optimal_n, endpoint=False)],
        color="red",
        label="Interpolation Nodes",
    )

    # Highlight areas with potential Gibbs effect
    ax.axvspan(
        np.pi / 2 - 0.1,
        np.pi / 2 + 0.1,
        color="green",
        alpha=0.3,
        label="Oscillation area 1",
    )
    ax.axvspan(
        3 * np.pi / 2 - 0.1,
        3 * np.pi / 2 + 0.1,
        color="orange",
        alpha=0.3,
        label="Oscillation area 2",
    )

    ax.set_title(f"Optimal Fourier Interpolation (n={optimal_n})", va="bottom")
    ax.legend(loc="upper right")

    if output_fp is not None:
        output_fp.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_fp)
    else:
        plt.show()


def display_results(
    optimal_n,
    optimal_theta0,
    optimal_a0,
    optimal_aj,
    optimal_bj,
    optimal_quality,
    output_fp,
):
    print(f"Optimal n: {optimal_n}")
    print(f"Optimal theta values: {optimal_theta0}")
    print(f"Optimal Fourier coefficients (a0): {optimal_a0}")
    print(f"Optimal Fourier coefficients (aj): {optimal_aj}")
    print(f"Optimal Fourier coefficients (bj): {optimal_bj}")
    print(f"Quality function value: {optimal_quality}")

    output_fp.parent.mkdir(parents=True, exist_ok=True)
    with open(output_fp, "w") as f:
        json.dump(
            {
                "n": optimal_n,
                "theta": optimal_theta0.tolist(),
                "a0": optimal_a0,
                "aj": optimal_aj.tolist(),
                "bj": optimal_bj.tolist(),
                "quality": optimal_quality,
            },
            f,
            indent=4,
        )


def main():
    args = parse_args()

    optimal_n = None
    optimal_theta0 = None
    optimal_a0 = None
    optimal_aj = None
    optimal_bj = None
    optimal_quality = float("inf")

    # Find the optimal solution
    for n in range(args.min_n, args.max_n + 1):
        theta, values = generate_nodes(n)
        a0, aj, bj = compute_fourier_coefficients(n, values)

        # Find the optimal theta0
        fine_theta = np.linspace(0, 2 * np.pi, 1000)
        interpolated_vals = [
            fourier_interpolation(n, a0, aj, bj, t) for t in fine_theta
        ]

        # Calculate the quality of the interpolation
        current_quality = quality(fine_theta, interpolated_vals, args.window_size)

        if current_quality < optimal_quality:
            optimal_quality = current_quality
            optimal_n = n
            optimal_theta0 = theta
            optimal_a0 = a0
            optimal_aj = aj
            optimal_bj = bj

    # Generate the interpolation for the optimal solution
    fine_theta = np.linspace(0, 2 * np.pi, 1000)
    interpolated_vals = [
        fourier_interpolation(optimal_n, optimal_a0, optimal_aj, optimal_bj, t)
        for t in fine_theta
    ]

    # Plot the interpolation
    plot_interpolation(fine_theta, interpolated_vals, optimal_n, args.plot_fp)

    display_results(
        optimal_n,
        optimal_theta0,
        optimal_a0,
        optimal_aj,
        optimal_bj,
        optimal_quality,
        args.output_fp,
    )


if __name__ == "__main__":
    main()
