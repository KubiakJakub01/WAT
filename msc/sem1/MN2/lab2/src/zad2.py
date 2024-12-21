import argparse
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt


def parse_args():
    parser = argparse.ArgumentParser(description="Cubic Spline Interpolation")
    parser.add_argument(
        "--data_fp",
        type=Path,
        default="data/dane_polar_F1.csv",
        help="Path to the input CSV file",
    )
    parser.add_argument(
        "--output_fp",
        type=Path,
        default="outputs/zad2/dane_polar2.csv",
        help="Path to the output CSV file",
    )
    parser.add_argument(
        "--table_fp",
        type=Path,
        default="outputs/zad2/max_deviations.csv",
        help="Path to the output max deviation table file",
    )
    parser.add_argument(
        "--plot_fp",
        type=Path,
        default="outputs/zad2/plot.png",
        help="Path to the output plot file",
    )
    return parser.parse_args()


def cubic_spline(theta, r):
    """Calculate coefficients for cubic spline interpolation.

    Args:
        theta (np.array): Array of theta values.
        r (np.array): Array of r(theta) values.

    Returns:
        tuple: Tuple containing coefficients a, b, c, d and h.
    """
    n = len(theta)

    h = [theta[i + 1] - theta[i] for i in range(n - 1)]

    A = np.zeros((n, n))
    b = np.zeros(n)

    A[0][0] = 1
    A[-1][-1] = 1

    for i in range(1, n - 1):
        A[i][i - 1] = h[i - 1]
        A[i][i] = 2 * (h[i - 1] + h[i])
        A[i][i + 1] = h[i]
        b[i] = 3 * ((r[i + 1] - r[i]) / h[i] - (r[i] - r[i - 1]) / h[i - 1])

    c = np.linalg.solve(A, b)

    a = r[:-1]
    b = np.zeros(n - 1)
    d = np.zeros(n - 1)

    for i in range(n - 1):
        b[i] = (r[i + 1] - r[i]) / h[i] - (h[i] / 3) * (2 * c[i] + c[i + 1])
        d[i] = (c[i + 1] - c[i]) / (3 * h[i])

    return a, b, c, d, h


def evaluate_spline(a, b, c, d, theta, theta_points):
    """Evaluate cubic spline interpolation for the given theta points.

    Args:
        a (np.array): Array of a coefficients.
        b (np.array): Array of b coefficients.
        c (np.array): Array of c coefficients.
        d (np.array): Array of d coefficients.
        theta (np.array): Array of theta values.
        theta_points (np.array): Array of theta points to evaluate.

    Returns:
        np.array: Array of interpolated r(theta) values.
    """
    results = []
    for theta_val in theta_points:
        for i in range(len(theta) - 1):
            if theta[i] <= theta_val <= theta[i + 1]:
                t = theta_val - theta[i]
                interpolated_val = a[i] + b[i] * t + c[i] * t**2 + d[i] * t**3
                results.append(interpolated_val)
                break
    return np.array(results)


def calculate_deviation(theta, r, a, b, c, d):
    """Calculate deviations between linear and cubic spline interpolation.

    Args:
        theta (np.array): Array of theta values.
        r (np.array): Array of r(theta) values.
        a (np.array): Array of a coefficients.
        b (np.array): Array of b coefficients.
        c (np.array): Array of c coefficients.
        d (np.array): Array of d coefficients.

    Returns:
        list: List of tuples containing interval and max deviation.
    """
    deviations = []
    for i in range(len(theta) - 1):
        linear_interp = np.linspace(r[i], r[i + 1], 100)
        theta_range = np.linspace(theta[i], theta[i + 1], 100)
        cubic_interp = evaluate_spline(a, b, c, d, theta, theta_range)

        deviation = np.abs(cubic_interp - linear_interp)
        max_deviation = np.max(deviation)
        deviations.append((theta[i], theta[i + 1], max_deviation))

    return deviations


def load_data(data_fp):
    """Load data from the given CSV file.

    Args:
        data_fp (str): Path to the input CSV file.

    Returns:
        tuple: Tuple containing theta and r values."""
    data = np.loadtxt(data_fp, delimiter=",")
    theta = data[:, 0]
    r = data[:, 1]
    return theta, r


def save_interpolated_data(new_theta, new_r, output_fp):
    """Save interpolated data to the given CSV file.

    Args:
        new_theta (np.array): Array of new theta values.
        new_r (np.array): Array of new r(theta) values.
        output_fp (str): Path to the output CSV file.
    """
    interpolated_data = np.column_stack((new_theta, new_r))
    output_fp.parent.mkdir(parents=True, exist_ok=True)
    np.savetxt(output_fp, interpolated_data, delimiter=",", fmt="%g")


def display_max_deviation_table(max_deviation_table, output_fp):
    """Display the max deviation table.

    Args:
        max_deviation_table (list): List of tuples containing interval and max deviation.
        output_fp (str): Path to the output max deviation table file.
    """
    print("Max Deviation Table:")
    print("Interval (θ_i, θ_{i+1}) | Max Deviation")
    for entry in max_deviation_table:
        print(f"[{entry[0]:.2f}, {entry[1]:.2f}] | {entry[2]:.6f}")

    output_fp.parent.mkdir(parents=True, exist_ok=True)
    with open(output_fp, "w") as f:
        f.write("Interval (θ_i, θ_{i+1}),Max Deviation\n")
        for entry in max_deviation_table:
            f.write(f"[{entry[0]:.2f}, {entry[1]:.2f}],{entry[2]:.6f}\n")


def plot_data(theta, r, new_theta, new_r, extended_theta, extended_r, output_fp):
    """Plot the original and interpolated data with extended interpolation.

    Args:
        theta (np.array): Array of theta values.
        r (np.array): Array of r(theta) values.
        new_theta (np.array): Array of new theta values for [0, π/4].
        new_r (np.array): Array of new r(theta) values for [0, π/4].
        extended_theta (np.array): Array of theta values for the full interpolation.
        extended_r (np.array): Array of r(theta) values for the full interpolation.
        output_fp (str): Path to the output plot file.
    """
    plt.figure(figsize=(10, 6))
    plt.plot(theta, r, "o", label="Original Data", markersize=8)
    plt.plot(
        extended_theta,
        extended_r,
        "-",
        label="Cubic Spline (Full Range)",
        color="blue",
        linewidth=2,
    )
    plt.plot(
        new_theta,
        new_r,
        "-",
        label="Cubic Spline [0, π/4]",
        color="orange",
        linewidth=2,
    )
    plt.xlabel("Theta (radians)")
    plt.ylabel("r(Theta)")
    plt.title("Cubic Spline Interpolation of Polar Data")
    plt.legend()
    plt.grid(True)
    if output_fp:
        output_fp.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_fp)
    else:
        plt.show()


if __name__ == "__main__":
    args = parse_args()
    theta, r = load_data(args.data_fp)
    a, b, c, d, h = cubic_spline(theta, r)
    new_theta = np.arange(0, np.pi / 4, 0.05)
    new_r = evaluate_spline(a, b, c, d, theta, new_theta)
    extended_theta = np.linspace(np.min(theta), np.max(theta), 500)
    extended_r = evaluate_spline(a, b, c, d, theta, extended_theta)
    save_interpolated_data(new_theta, new_r, args.output_fp)
    max_deviation_table = calculate_deviation(theta, r, a, b, c, d)
    display_max_deviation_table(max_deviation_table, args.table_fp)
    plot_data(theta, r, new_theta, new_r, extended_theta, extended_r, args.plot_fp)
