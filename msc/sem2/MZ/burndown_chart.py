import matplotlib.pyplot as plt
import numpy as np

# Dane sprintu
dni = [0, 1, 2, 3, 4, 5, 6, 7]
pozostalo_godzin = [49, 43, 35, 28, 22, 14, 7, 0]

# Linia idealna (prosta z 49 do 0)
idealna_linia = np.linspace(49, 0, 8)

# Tworzenie wykresu
plt.figure(figsize=(10, 6))

# Wykres rzeczywistego postępu (niebieska linia schodkowa)
plt.plot(dni, pozostalo_godzin, 'b-o', linewidth=2, markersize=6, label='Rzeczywisty postęp')

# Wykres idealnego postępu (szara prosta linia)
plt.plot(dni, idealna_linia, 'gray', linewidth=1, linestyle='--', label='Idealny postęp')

# Ustawienia wykresu
plt.title('Wykres Wypalania Sprintu (Burndown Chart)', fontsize=16, fontweight='bold')
plt.xlabel('Dni sprintu', fontsize=12, fontweight='bold')
plt.ylabel('Pozostało godzin', fontsize=12, fontweight='bold')

# Ustawienia osi
plt.xlim(-0.5, 7.5)
plt.ylim(0, 55)
plt.xticks(dni)
plt.yticks(range(0, 60, 10))

# Siatka
plt.grid(True, alpha=0.3)

# Legenda
plt.legend()

# Dodanie wartości na punktach
for i, v in enumerate(pozostalo_godzin):
    plt.annotate(f'{v}h', (dni[i], v), textcoords="offset points", xytext=(0,10), ha='center')

# Wyświetlenie wykresu
plt.tight_layout()
# plt.show()

# Opcjonalnie: zapisanie do pliku
plt.savefig('burndown_chart.png', dpi=300, bbox_inches='tight')
