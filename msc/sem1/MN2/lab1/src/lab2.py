import argparse

import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import BarycentricInterpolator


def f(x):
    if x < -5 or x > 4:
        return 0
    elif -5 <= x <= -3:
        return (x + 5) * (x + 3)
    elif -3 < x <= -1:
        return x
    elif -1 < x <= 4:
        return (x + 1) * (x - 4)


f_vectorized = np.vectorize(f)


def polynomial_interpolation(x_nodes, y_nodes):
    interpolant = BarycentricInterpolator(x_nodes, y_nodes)
    return interpolant


def quality_check(x_values, f_values, interpolant_values):
    error = np.abs(f_values - interpolant_values)
    return np.sum(error)


def interpolation_task(
    n_nodes,
    plot: bool = False,
    plot_equidistant: bool = False,
    plot_chebyshev: bool = False,
):
    x_values = np.linspace(-5, 4, 500)
    f_values = f_vectorized(x_values)

    x_nodes_equidistant = np.linspace(-5, 4, n_nodes)
    y_nodes_equidistant = f_vectorized(x_nodes_equidistant)
    interpolant_equidistant = polynomial_interpolation(
        x_nodes_equidistant, y_nodes_equidistant
    )
    interpolant_values_equidistant = interpolant_equidistant(x_values)

    x_nodes_chebyshev = np.cos(np.linspace(0, np.pi, n_nodes)) * 4.5 + -0.5
    y_nodes_chebyshev = f_vectorized(x_nodes_chebyshev)
    interpolant_chebyshev = polynomial_interpolation(
        x_nodes_chebyshev, y_nodes_chebyshev
    )
    interpolant_values_chebyshev = interpolant_chebyshev(x_values)

    quality_equidistant = quality_check(
        x_values, f_values, interpolant_values_equidistant
    )
    quality_chebyshev = quality_check(x_values, f_values, interpolant_values_chebyshev)

    if plot:
        plt.figure(figsize=(10, 6))
        plt.plot(
            x_values,
            f_values,
            label="Original function f(x)",
            color="black",
            linewidth=2,
        )
        if plot_equidistant:
            plt.plot(
                x_values,
                interpolant_values_equidistant,
                label=f"Equidistant interpolation (Quality: {quality_equidistant:.2f})",
                linestyle="--",
            )
            plt.scatter(
                x_nodes_equidistant,
                y_nodes_equidistant,
                color="red",
                label="Equidistant nodes",
                zorder=5,
            )
        if plot_chebyshev:
            plt.plot(
                x_values,
                interpolant_values_chebyshev,
                label=f"Chebyshev interpolation (Quality: {quality_chebyshev:.2f})",
                linestyle="--",
            )
            plt.scatter(
                x_nodes_chebyshev,
                y_nodes_chebyshev,
                color="blue",
                label="Chebyshev nodes",
                zorder=5,
            )

        plt.title("Polynomial Interpolation of f(x)")
        plt.xlabel("x")
        plt.ylabel("f(x)")
        plt.legend()
        plt.grid(True)
        plt.show()

    return (
        quality_equidistant,
        quality_chebyshev,
        x_nodes_equidistant,
        x_nodes_chebyshev,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--n_nodes",
        type=int,
        default=None,
        help="Number of nodes used for interpolation",
    )
    parser.add_argument("--plot_equidistant", action="store_true", default=False)
    parser.add_argument("--plot_chebyshev", action="store_true", default=False)
    args = parser.parse_args()

    best_n_equidistant, best_score_equidistant = 0, float("inf")
    best_n_chebyshev, best_score_chebyshev = 0, float("inf")
    for i in range(5, 31):
        quality_equidistant, quality_chebyshev, _, _ = interpolation_task(n_nodes=i)
        if quality_equidistant < best_score_equidistant:
            best_score_equidistant = quality_equidistant
            best_n_equidistant = i
        if quality_chebyshev < best_score_chebyshev:
            best_score_chebyshev = quality_chebyshev
            best_n_chebyshev = i

    print(
        f"Best equidistant interpolation: n={best_n_equidistant} score={best_score_equidistant}"
    )
    print(
        f"Best chebyshev interpolation: n={best_n_chebyshev} score={best_score_chebyshev}"
    )

    if args.n_nodes is not None:
        interpolation_task(
            n_nodes=args.n_nodes,
            plot=True,
            plot_equidistant=args.plot_equidistant,
            plot_chebyshev=args.plot_chebyshev,
        )
