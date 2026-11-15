"""
Implementación desde cero del Problema del Agente Viajero (TSP) Euclidiano 2D
y Recocido Simulado (Simulated Annealing) con operador de vecindad 2-opt.

Incluye:
- Generación determinista de instancias fijas para n in {5, 10, 15}.
- Cálculo exacto del óptimo global de referencia mediante programación dinámica (Held-Karp).
- Operador 2-opt en O(1) para la evaluación incremental de Delta E.
- Recocido Simulado con criterio de aceptación de Metropolis y enfriamiento geométrico.
"""

from __future__ import annotations

import json
import math
import random
from pathlib import Path

import numpy as np

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
INSTANCES_PATH = DATA_DIR / "tsp_instances.json"

TAMANOS = [5, 10, 15]
INSTANCE_SEED_BASE = 100


def generar_instancia_tsp(n: int, seed: int, max_coord: float = 1000.0) -> dict:
    """Genera una instancia TSP euclidiana 2D en [0, max_coord]^2 con su matriz de distancias."""
    rng = random.Random(seed)
    coords = [
        [round(rng.uniform(0.0, max_coord), 2), round(rng.uniform(0.0, max_coord), 2)]
        for _ in range(n)
    ]
    dist_matrix = np.zeros((n, n), dtype=float)
    for i in range(n):
        for j in range(n):
            if i != j:
                dist_matrix[i, j] = math.hypot(
                    coords[i][0] - coords[j][0],
                    coords[i][1] - coords[j][1],
                )
    opt_cost = held_karp_optimo(dist_matrix)
    return {
        "n": n,
        "seed_instancia": seed,
        "max_coord": max_coord,
        "coords": coords,
        "dist_matrix": np.round(dist_matrix, 6).tolist(),
        "costo_optimo_exacto": round(float(opt_cost), 4),
    }


def held_karp_optimo(dist_matrix: np.ndarray) -> float:
    """Calcula el costo del tour TSP óptimo exacto usando programación dinámica Held-Karp."""
    n = len(dist_matrix)
    if n <= 2:
        return float(np.sum(dist_matrix))

    # Fija ciudad 0 como inicio; estados sobre ciudades 1..n-1 (m = n - 1 bits)
    m = n - 1
    full_mask = (1 << m) - 1
    inf = float("inf")
    dp = np.full((1 << m, m), inf, dtype=float)

    for j in range(m):
        dp[1 << j, j] = dist_matrix[0, j + 1]

    for mask in range(1, 1 << m):
        for last in range(m):
            if not (mask & (1 << last)):
                continue
            prev_cost = dp[mask, last]
            if prev_cost == inf:
                continue
            rem = full_mask ^ mask
            while rem:
                lsb = rem & -rem
                nxt = lsb.bit_length() - 1
                new_mask = mask | lsb
                cand = prev_cost + dist_matrix[last + 1, nxt + 1]
                if cand < dp[new_mask, nxt]:
                    dp[new_mask, nxt] = cand
                rem ^= lsb

    best = inf
    for last in range(m):
        total = dp[full_mask, last] + dist_matrix[last + 1, 0]
        if total < best:
            best = total
    return float(best)


def calcular_costo(ruta: list[int], dist_matrix: np.ndarray) -> float:
    """Calcula el costo total cerrado de una permutación de ciudades."""
    n = len(ruta)
    return float(sum(dist_matrix[ruta[i], ruta[(i + 1) % n]] for i in range(n)))


def vecino_2opt(ruta: list[int], dist_matrix: np.ndarray, rng: random.Random) -> tuple[int, int, float]:
    """
    Selecciona aleatoriamente dos índices i < j válidos y calcula en O(1)
    el cambio de costo Delta E al invertir el subsegmento ruta[i:j+1].
    """
    n = len(ruta)
    while True:
        i = rng.randrange(0, n - 1)
        j = rng.randrange(i + 1, n)
        if not (i == 0 and j == n - 1):
            break

    a, b = ruta[i - 1], ruta[i]
    c, d = ruta[j], ruta[(j + 1) % n]
    delta = (dist_matrix[a, c] + dist_matrix[b, d]) - (dist_matrix[a, b] + dist_matrix[c, d])
    return i, j, float(delta)


def recocido_simulado_tsp(
    dist_matrix: np.ndarray,
    T0: float,
    alpha: float = 0.85,
    max_iter: int | None = None,
    steps_per_epoch: int | None = None,
    seed: int = 0,
) -> dict:
    """
    Ejecuta Recocido Simulado con vecindario 2-opt sobre una instancia TSP.

    Parámetros:
    - dist_matrix: matriz de distancias n x n.
    - T0: temperatura inicial.
    - alpha: razón de enfriamiento geométrico (T_{k+1} = alpha * T_k por época).
    - max_iter: presupuesto total de evaluaciones 2-opt (por defecto 18 * n, i.e., 18 épocas de n pasos).
    - steps_per_epoch: propuestas 2-opt por nivel de temperatura (por defecto n).
    - seed: semilla para reproducibilidad de ruta inicial y decisiones estocásticas.

    Retorna un diccionario con el costo del estado al final del enfriamiento ('costo_final'),
    el mejor histórico visitado ('mejor_costo'), la ruta final y la temperatura final.
    """
    rng = random.Random(seed)
    n = len(dist_matrix)
    if steps_per_epoch is None:
        steps_per_epoch = n
    if max_iter is None:
        max_iter = 18 * n

    n_epochs = max(1, max_iter // steps_per_epoch)

    ruta = list(range(n))
    rng.shuffle(ruta)
    costo_actual = calcular_costo(ruta, dist_matrix)
    mejor_costo = costo_actual
    T = float(T0)
    aceptados = 0

    for _ in range(n_epochs):
        for _ in range(steps_per_epoch):
            i, j, delta = vecino_2opt(ruta, dist_matrix, rng)
            if delta <= 0.0 or (T > 1e-12 and rng.random() < math.exp(-delta / T)):
                ruta[i : j + 1] = reversed(ruta[i : j + 1])
                costo_actual += delta
                aceptados += 1
                if costo_actual < mejor_costo:
                    mejor_costo = costo_actual
        T *= alpha

    # Recálculo exacto para evitar deriva numérica por sumas flotantes
    costo_final = calcular_costo(ruta, dist_matrix)
    return {
        "costo_final": costo_final,
        "mejor_costo": float(mejor_costo),
        "temperatura_final": T,
        "aceptados": aceptados,
        "iteraciones": n_epochs * steps_per_epoch,
        "ruta_final": ruta,
    }


def generar_y_guardar_instancias(ruta_salida: Path = INSTANCES_PATH) -> dict[int, dict]:
    """Genera las instancias fijas para n in {5, 10, 15} y las guarda en JSON."""
    ruta_salida.parent.mkdir(parents=True, exist_ok=True)
    instancias = {}
    for n in TAMANOS:
        inst = generar_instancia_tsp(n=n, seed=INSTANCE_SEED_BASE + n)
        instancias[str(n)] = inst
    with open(ruta_salida, "w", encoding="utf-8") as f:
        json.dump(instancias, f, indent=2, ensure_ascii=False)
    return {int(k): v for k, v in instancias.items()}


def cargar_instancias(ruta_entrada: Path = INSTANCES_PATH) -> dict[int, dict]:
    """Carga las instancias TSP desde JSON (o las genera si aún no existen)."""
    if not ruta_entrada.exists():
        return generar_y_guardar_instancias(ruta_entrada)
    with open(ruta_entrada, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {int(k): v for k, v in data.items()}


if __name__ == "__main__":
    insts = generar_y_guardar_instancias()
    print(f"Instancias generadas y guardadas en {INSTANCES_PATH}:")
    for n, info in insts.items():
        print(f"  n={n:2d} | seed={info['seed_instancia']} | óptimo exacto (Held-Karp) = {info['costo_optimo_exacto']:.4f}")
