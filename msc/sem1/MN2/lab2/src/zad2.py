import argparse
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt


def parse_args():
    parser = argparse.ArgumentParser(description="Cubic and Linear Spline Interpolation")
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
    parser.add_argument(
        "--fourier_plot_fp",
        type=Path,
        default="outputs/zad2/fourier_plot.png",
        help="Path to the Fourier interpolation plot file",
    )
    return parser.parse_args()


def linear_spline(theta, r, theta_points):
    """Evaluate linear spline interpolation for the given theta points."""
    results = []
    for theta_val in theta_points:
        for i in range(len(theta) - 1):
            if theta[i] <= theta_val <= theta[i + 1]:
                t = (theta_val - theta[i]) / (theta[i + 1] - theta[i])
                interpolated_val = (1 - t) * r[i] + t * r[i + 1]
                results.append(interpolated_val)
                break
    return np.array(results)


def fourier_coefficients(theta, r, n_terms):
    """Calculate Fourier coefficients for the given data."""
    a0 = (1 / len(theta)) * np.sum(r)
    a = []
    b = []
    for n in range(1, n_terms + 1):
        an = (2 / len(theta)) * np.sum(r * np.cos(n * theta))
        bn = (2 / len(theta)) * np.sum(r * np.sin(n * theta))
        a.append(an)
        b.append(bn)
    return a0, np.array(a), np.array(b)


def evaluate_fourier(a0, a_coeffs, b_coeffs, theta_points):
    """Evaluate Fourier series interpolation for the given theta points."""
    result = np.full_like(theta_points, a0)
    for n in range(1, len(a_coeffs) + 1):
        result += a_coeffs[n - 1] * np.cos(n * theta_points) + b_coeffs[n - 1] * np.sin(n * theta_points)
    return result


def cubic_spline(theta, r):
    """Calculate coefficients for cubic spline interpolation."""
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
    """Evaluate cubic spline interpolation for the given theta points."""
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
    """Calculate deviations between linear and cubic spline interpolation."""
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
    """Load data from the given CSV file."""
    data = np.loadtxt(data_fp, delimiter=",")
    theta = data[:, 0]
    r = data[:, 1]
    return theta, r


def save_interpolated_data(new_theta, new_r, output_fp):
    """Save interpolated data to the given CSV file."""
    interpolated_data = np.column_stack((new_theta, new_r))
    output_fp.parent.mkdir(parents=True, exist_ok=True)
    np.savetxt(output_fp, interpolated_data, delimiter=",", fmt="%g")


def display_max_deviation_table(max_deviation_table, output_fp):
    """Display the max deviation table."""
    print("Max Deviation Table:")
    print("Interval (\u03b8_i, \u03b8_{i+1}) | Max Deviation")
    for entry in max_deviation_table:
        print(f"[{entry[0]:.2f}, {entry[1]:.2f}] | {entry[2]:.6f}")

    output_fp.parent.mkdir(parents=True, exist_ok=True)
    with open(output_fp, "w") as f:
        f.write("Interval (\u03b8_i, \u03b8_{i+1}),Max Deviation\n")
        for entry in max_deviation_table:
            f.write(f"[{entry[0]:.2f}, {entry[1]:.2f}],{entry[2]:.6f}\n")


def plot_interpolations(theta, r, theta_points, fourier_r, cubic_r, linear_r, output_fp):
    """Plot Fourier, cubic spline, and linear spline interpolations along with original data."""
    plt.figure(figsize=(10, 6))
    plt.plot(theta, r, "o", label="Original Data", markersize=8)
    plt.plot(
        theta_points,
        fourier_r,
        "-",
        label="Fourier Interpolation",
        color="blue",
        linewidth=2,
    )
    plt.plot(
        theta_points,
        cubic_r,
        "-",
        label="Cubic Spline Interpolation",
        color="orange",
        linewidth=2,
    )
    plt.plot(
        theta_points,
        linear_r,
        "--",
        label="Linear Spline Interpolation",
        color="green",
        linewidth=2,
    )
    plt.xlabel("Theta (radians)")
    plt.ylabel("r(Theta)")
    plt.title("Fourier, Cubic Spline, and Linear Spline Interpolation of Polar Data")
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
    extended_theta = np.linspace(np.min(theta), np.max(theta), 500)
    new_r_cubic = evaluate_spline(a, b, c, d, theta, extended_theta)
    new_r_linear = linear_spline(theta, r, extended_theta)
    a0, a_coeffs, b_coeffs = fourier_coefficients(theta, r, n_terms=5)
    print("Fourier Coefficients:")
    print(f"a0: {a0}")
    print(f"a: {a_coeffs}")
    print(f"b: {b_coeffs}")
    fourier_r = evaluate_fourier(a0, a_coeffs, b_coeffs, extended_theta)
    max_deviation_table = calculate_deviation(theta, r, a, b, c, d)
    save_interpolated_data(extended_theta, new_r_cubic, args.output_fp)
    display_max_deviation_table(max_deviation_table, args.table_fp)
    plot_interpolations(theta, r, extended_theta, fourier_r, new_r_cubic, new_r_linear, args.plot_fp)
