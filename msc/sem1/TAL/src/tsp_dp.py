from .utils import euclidean_distance


def tsp_dynamic_programming(city_coords: dict[str, tuple[float, float]]) -> float:
    """Solve the Travelling Salesman Problem using dynamic programming.

    Args:
        city_coords: Dictionary containing the coordinates of each city

    Returns:
        Minimum cost to visit all cities
    """
    num_cities = len(city_coords)
    cities_names = list(city_coords.keys())

    # Pre-compute distances between all pairs of cities
    distances = [[0] * num_cities for _ in range(num_cities)]
    for i in range(num_cities):
        for j in range(num_cities):
            distances[i][j] = euclidean_distance(city_coords[cities_names[i]], city_coords[cities_names[j]])

    # Initialize the DP table
    dp = [[float('inf')] * num_cities for _ in range(1 << num_cities)]
    dp[1][0] = 0

    # Fill the DP table
    for mask in range(1 << num_cities):
        for last in range(num_cities):
            if not (mask & (1 << last)):
                continue
            for next_city in range(num_cities):
                if mask & (1 << next_city):
                    continue
                new_mask = mask | (1 << next_city)
                dp[new_mask][next_city] = min(
                    dp[new_mask][next_city],
                    dp[mask][last] + distances[last][next_city]
                )

    # Find the minimum cost to visit all cities
    min_cost = float('inf')
    final_mask = (1 << num_cities) - 1
    for last in range(1, num_cities):
        min_cost = min(min_cost, dp[final_mask][last] + distances[last][0])

    return min_cost
