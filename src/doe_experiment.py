"""
Ejecución del Diseño Factorial Completo 3×3 (Opción A) para el ajuste de
temperatura inicial T0 en Recocido Simulado con 2-opt sobre TSP.

- Matrícula: 2225437 -> r = 0.7148901388751733
- Niveles de Temperatura (Opción A):
    Bajo  = 0.3 * r
    Medio = 0.3 * r + 0.3
    Alto  = 0.3 * r + 0.6
- Rango de temperatura: [T_min, T_max] = [10.0, 500.0]
- Bloques: n in {5, 10, 15}
- Réplicas: 10 corridas independientes por punto de diseño (90 corridas en total).
"""

from __future__ import annotations

import json
import random
import time
from pathlib import Path

import numpy as np
import pandas as pd

from tsp_sa import cargar_instancias, recocido_simulado_tsp

ROOT_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = ROOT_DIR / "results"

MATRICULA = 2225437
T_MIN = 1.0
T_MAX = 150.0
ALPHA = 0.88
EPOCHS = 18
N_REPLICAS = 10
TAMANOS = [5, 10, 15]


def generar_niveles_temperatura(
    matricula: int = MATRICULA,
    t_min: float = T_MIN,
    t_max: float = T_MAX,
) -> tuple[float, list[dict]]:
    """Genera un único valor r ~ Uniforme(0, 1) con la matrícula y calcula los 3 niveles (Opción A)."""
    random.seed(matricula)
    r = random.random()

    definiciones = [
        ("Bajo", 0.3 * r),
        ("Medio", 0.3 * r + 0.3),
        ("Alto", 0.3 * r + 0.6),
    ]
    niveles = []
    for nombre, fraccion in definiciones:
        temp = t_min + fraccion * (t_max - t_min)
        niveles.append(
            {
                "nivel": nombre,
                "fraccion": fraccion,
                "temperatura": temp,
            }
        )
    return r, niveles


def run_experiment() -> pd.DataFrame:
    """Ejecuta las 90 corridas del diseño factorial 3×3 y guarda results/raw_runs.csv."""
    instancias = cargar_instancias()
    r, niveles = generar_niveles_temperatura()

    print(f"Matrícula: {MATRICULA}")
    print(f"Valor único r = {r:.16f}")
    print(f"Rango de temperatura: [{T_MIN}, {T_MAX}]")
    for lvl in niveles:
        print(f"  {lvl['nivel']:5s} -> fracción = {lvl['fraccion']:.6f}, T0 = {lvl['temperatura']:.4f}")

    registros = []
    run_id = 1
    for n in TAMANOS:
        dist_matrix = np.array(instancias[n]["dist_matrix"], dtype=float)
        opt_exacto = float(instancias[n]["costo_optimo_exacto"])
        max_iter = EPOCHS * n

        for idx_lvl, lvl in enumerate(niveles):
            for rep in range(N_REPLICAS):
                seed = 10000 + 1000 * n + 100 * idx_lvl + rep
                t0_clock = time.perf_counter()
                res = recocido_simulado_tsp(
                    dist_matrix=dist_matrix,
                    T0=lvl["temperatura"],
                    alpha=ALPHA,
                    max_iter=max_iter,
                    steps_per_epoch=n,
                    seed=seed,
                )
                elapsed_ms = (time.perf_counter() - t0_clock) * 1000.0
                costo = float(res["costo_final"])
                gap_pct = 100.0 * (costo - opt_exacto) / opt_exacto

                registros.append(
                    {
                        "run_id": run_id,
                        "tamano": n,
                        "nivel_temperatura": lvl["nivel"],
                        "fraccion": lvl["fraccion"],
                        "temperatura": lvl["temperatura"],
                        "replica": rep + 1,
                        "seed": seed,
                        "costo": costo,
                        "mejor_costo_historico": float(res["mejor_costo"]),
                        "optimo_exacto": opt_exacto,
                        "gap_optimo_pct": gap_pct,
                        "temperatura_final": float(res["temperatura_final"]),
                        "tiempo_ms": elapsed_ms,
                    }
                )
                run_id += 1

    df = pd.DataFrame(registros)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    raw_path = RESULTS_DIR / "raw_runs.csv"
    df.to_csv(raw_path, index=False)

    config = {
        "matricula": MATRICULA,
        "r": r,
        "opcion": "A - Diseño Factorial Completo 3x3",
        "t_min": T_MIN,
        "t_max": T_MAX,
        "alpha": ALPHA,
        "epochs": EPOCHS,
        "steps_per_epoch_rule": "n",
        "n_replicas": N_REPLICAS,
        "total_corridas": len(df),
        "niveles": niveles,
    }
    with open(RESULTS_DIR / "experiment_config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    print(f"\nExperimento completado: {len(df)} corridas guardadas en {raw_path}")
    return df


if __name__ == "__main__":
    run_experiment()
