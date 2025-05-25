import math

import numpy as np
from scipy.optimize import minimize

# --- Dane wejściowe ---

# Prawdopodobieństwa przejść p_ij (moduły indeksowane od 0 do 8)
# Moduł 1 -> indeks 0, ..., Moduł 9 -> indeks 8
ADJ = {
    0: [(1, 0.4), (2, 0.6)],  # Moduł 1
    1: [(3, 0.7), (6, 0.3)],  # Moduł 2
    2: [(3, 0.3), (4, 0.7)],  # Moduł 3
    3: [(4, 0.3), (5, 0.2), (6, 0.5)],  # Moduł 4
    4: [(7, 1.0)],  # Moduł 5
    5: [(6, 0.4), (7, 0.6)],  # Moduł 6
    6: [(8, 1.0)],  # Moduł 7
    7: [(6, 0.2), (8, 0.8)],  # Moduł 8
    8: [],  # Moduł 9 (ujście)
}
SOURCE_NODE = 0
SINK_NODE = 8
NUM_MODULES = 9

# Parametry kosztu Ki(Ri) = Si + ai * exp(betai * Ri)
# Indeks i odpowiada modułowi i+1
S_params = np.array(
    [1000.0, 400.0, 1500.0, 2500.0, 900.0, 300.0, 1300.0, 2400.0, 800.0]
)
a_params = np.array([50.0, 35.0, 25.0, 30.0, 40.0, 35.0, 20.0, 30.0, 60.0])
beta_params = np.array([5.0, 2.0, 8.0, 10.0, 4.0, 3.0, 9.0, 12.0, 5.0])

# Ograniczenia
R_MIN_CONSTRAINT = 0.95
K_MAX_CONSTRAINT = 4500000.0

# --- Wyszukiwanie ścieżek i obliczanie d_q ---
paths_details = []  # Lista кортежей: (lista_modułów_w_ścieżce, prawdopodobieństwo_d_q)


def find_all_paths_recursive(current_node_idx, current_path_modules, current_d_q_prob):
    current_path_modules.append(current_node_idx)

    if current_node_idx == SINK_NODE:
        paths_details.append((list(current_path_modules), current_d_q_prob))
        current_path_modules.pop()
        return

    if current_node_idx in ADJ:
        for neighbor_idx, transition_prob in ADJ[current_node_idx]:
            # Aby uniknąć nieskończonych pętli i zapewnić "logiczne ścieżki", zakładamy ścieżki proste
            if neighbor_idx not in current_path_modules:
                find_all_paths_recursive(
                    neighbor_idx,
                    current_path_modules,
                    current_d_q_prob * transition_prob,
                )

    current_path_modules.pop()


# Inicjalizacja wyszukiwania ścieżek
find_all_paths_recursive(SOURCE_NODE, [], 1.0)

if not paths_details:
    print(
        "Ostrzeżenie: Nie znaleziono żadnych ścieżek od modułu startowego do końcowego."
    )
    print(f"Moduł startowy: {SOURCE_NODE+1}, Moduł końcowy: {SINK_NODE+1}")
    # exit() # Można przerwać, jeśli brak ścieżek uniemożliwia dalsze obliczenia


# --- Funkcje do obliczania K(R) i R(R) ---
def calculate_K(R_vector):
    """Oblicza całkowity koszt K(R)"""
    if len(R_vector) != NUM_MODULES:
        raise ValueError(f"Wektor R_vector musi mieć długość {NUM_MODULES}")
    K_i = S_params + a_params * np.exp(beta_params * R_vector)
    return np.sum(K_i)


def calculate_R(R_vector):
    """Oblicza całkowitą niezawodność R(R)"""
    if len(R_vector) != NUM_MODULES:
        raise ValueError(f"Wektor R_vector musi mieć długość {NUM_MODULES}")
    if not paths_details:  # Jeśli nie ma ścieżek, niezawodność programu = 0
        return 0.0

    total_reliability = 0.0
    for path_modules, d_q in paths_details:
        path_reliability_product = 1.0
        for module_idx in path_modules:
            path_reliability_product *= R_vector[module_idx]
        total_reliability += d_q * path_reliability_product
    return total_reliability


# --- Normalizacja i funkcja celu ---

# Granice normalizacji
# K_norm = (K(R) - K_NORM_MIN_VAL) / (K_NORM_MAX_VAL - K_NORM_MIN_VAL)
# R_norm = (R(R) - R_NORM_MIN_VAL) / (R_NORM_MAX_VAL - R_NORM_MIN_VAL)

K_NORM_MIN_VAL = np.sum(S_params + a_params * np.exp(beta_params * 0.0))  # K gdy Ri=0
K_NORM_MAX_VAL = K_MAX_CONSTRAINT

R_NORM_MIN_VAL = R_MIN_CONSTRAINT
R_NORM_MAX_VAL = 1.0  # Teoretyczne maksimum dla R(R)

# Zabezpieczenie przed dzieleniem przez zero, jeśli K_NORM_MIN_VAL == K_NORM_MAX_VAL lub R_NORM_MIN_VAL == R_NORM_MAX_VAL
# (mało prawdopodobne w tym problemie, ale dobra praktyka)
K_NORM_DENOMINATOR = (
    K_NORM_MAX_VAL - K_NORM_MIN_VAL if K_NORM_MAX_VAL > K_NORM_MIN_VAL else 1.0
)
R_NORM_DENOMINATOR = (
    R_NORM_MAX_VAL - R_NORM_MIN_VAL if R_NORM_MAX_VAL > R_NORM_MIN_VAL else 1.0
)


def objective_function(R_vector_candidate):
    # Upewnij się, że wartości R_i są w granicach [0,1] (choć optymalizator powinien to robić)
    R_vector = np.clip(R_vector_candidate, 0.0, 1.0)

    k_val = calculate_K(R_vector)
    r_val = calculate_R(R_vector)

    # Normalizacja
    # Należy uważać, aby k_val i r_val mieściły się w przewidywanych granicach normalizacji,
    # w przeciwnym razie znormalizowane wartości mogą wyjść poza [0,1].
    # Dla funkcji odległości nie jest to krytyczne, ale dla interpretacji może być.

    k_norm = (k_val - K_NORM_MIN_VAL) / K_NORM_DENOMINATOR
    r_norm = (r_val - R_NORM_MIN_VAL) / R_NORM_DENOMINATOR

    # Odległość od punktu idealnego (R_norm=1, K_norm=0)
    # Idealny R_norm to 1 (maksymalna niezawodność po normalizacji)
    # Idealny K_norm to 0 (minimalny koszt po normalizacji)
    distance = math.sqrt((r_norm - 1.0) ** 2 + (k_norm - 0.0) ** 2)
    return distance


# --- Optymalizacja ---

# Ograniczenia dla scipy.optimize.minimize
# 1. R(R) >= R_MIN_CONSTRAINT  =>  R(R) - R_MIN_CONSTRAINT >= 0
# 2. K(R) <= K_MAX_CONSTRAINT  =>  K_MAX_CONSTRAINT - K(R) >= 0
constraints = [
    {
        "type": "ineq",
        "fun": lambda R_vec: calculate_R(np.clip(R_vec, 0, 1)) - R_MIN_CONSTRAINT,
    },
    {
        "type": "ineq",
        "fun": lambda R_vec: K_MAX_CONSTRAINT - calculate_K(np.clip(R_vec, 0, 1)),
    },
]

# Granice dla każdej zmiennej R_i (0 <= R_i <= 1)
bounds = [(0.0, 1.0) for _ in range(NUM_MODULES)]

# Początkowy wektor R (np. wysokie wartości, aby spróbować spełnić R_MIN_CONSTRAINT)
# R_min_constr = 0.95. Przyjmując średnią długość ścieżki np. 5, Ri ~ 0.95^(1/5) ~ 0.989
initial_R_guess = np.array([0.98] * NUM_MODULES)


print("Rozpoczynanie optymalizacji...")
# Sprawdzenie, czy są ścieżki, aby uniknąć problemów w funkcjach celu
if not paths_details:
    print(
        "Nie można przeprowadzić optymalizacji, ponieważ nie znaleziono ścieżek w grafie."
    )
else:
    solution = minimize(
        objective_function,
        initial_R_guess,
        method="SLSQP",  # Metoda wspierająca ograniczenia i granice
        bounds=bounds,
        constraints=constraints,
        options={
            "disp": True,
            "maxiter": 1000,
            "ftol": 1e-9,
        },  # Zwiększono maxiter i zmieniono ftol
    )

    if solution.success:
        optimal_R_vector = np.clip(solution.x, 0, 1)  # Dla pewności
        final_K = calculate_K(optimal_R_vector)
        final_R = calculate_R(optimal_R_vector)

        print("\n--- Wyniki Optymalizacji ---")
        print(f"Status optymalizacji: {solution.message}")
        print(f"Znaleziony optymalny wektor R*: {optimal_R_vector}")
        for i, r_val in enumerate(optimal_R_vector):
            print(f"  R_{i+1}* = {r_val:.6f}")

        print(f"\nKońcowa obliczona niezawodność R(R*): {final_R:.6f}")
        print(f"Końcowy obliczony koszt K(R*): {final_K:.2f} zł")

        # Sprawdzenie ograniczeń
        print("\nSprawdzenie ograniczeń dla znalezionego rozwiązania:")
        print(
            f"  R(R*) >= {R_MIN_CONSTRAINT}: {final_R >= R_MIN_CONSTRAINT} ({final_R:.6f} >= {R_MIN_CONSTRAINT})"
        )
        print(
            f"  K(R*) <= {K_MAX_CONSTRAINT}: {final_K <= K_MAX_CONSTRAINT} ({final_K:.2f} <= {K_MAX_CONSTRAINT})"
        )
        for i, r_val in enumerate(optimal_R_vector):
            print(f"  0 <= R_{i+1}* <= 1: {0 <= r_val <= 1}")

        # Znormalizowane wartości dla znalezionego rozwiązania
        final_k_norm = (final_K - K_NORM_MIN_VAL) / K_NORM_DENOMINATOR
        final_r_norm = (final_R - R_NORM_MIN_VAL) / R_NORM_DENOMINATOR
        print(f"\nZnormalizowana niezawodność R_norm(R*): {final_r_norm:.6f}")
        print(f"Znormalizowany koszt K_norm(R*): {final_k_norm:.6f}")
        final_distance = math.sqrt(
            (final_r_norm - 1.0) ** 2 + (final_k_norm - 0.0) ** 2
        )
        print(
            f"Minimalna odległość do punktu idealnego (1,0) w przestrzeni znormalizowanej: {final_distance:.6f}"
        )

    else:
        print("\nOptymalizacja nie powiodła się.")
        print(f"Status: {solution.message}")
        print(f"Ostatni wektor R: {solution.x}")
        if solution.x is not None and len(solution.x) == NUM_MODULES:
            last_K = calculate_K(solution.x)
            last_R = calculate_R(solution.x)
            print(f"Ostatnia obliczona niezawodność R(R): {last_R:.6f}")
            print(f"Ostatni obliczony koszt K(R): {last_K:.2f} zł")


print(f"\nZnalezione ścieżki (liczba: {len(paths_details)}):")
for i, (p, dq) in enumerate(paths_details):
    path_nodes = [
        node_idx + 1 for node_idx in p
    ]  # Konwersja na 1-indeksowanie dla wyświetlenia
    print(
        f"  Ścieżka {i+1}: {path_nodes}, d_q = {dq:.4f}"
    )  # Można odkomentować, aby zobaczyć wszystkie ścieżki
