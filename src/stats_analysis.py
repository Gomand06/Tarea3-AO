"""
Análisis estadístico para la Tarea 3 (DOE - Opción A):
- ANOVA de dos factores (temperatura, tamaño e interacción) con statsmodels (Tipo II).
- Estimación no paramétrica vía Bootstrap (B = 10,000 remuestreos) de la mediana e IC 95%.
- Selección de la temperatura óptima por cada tamaño de problema (n = 5, 10, 15).
"""

from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", os.path.join(os.environ.get("TEMP", "."), "mplconfig"))

import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.formula.api import ols

ROOT_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = ROOT_DIR / "results"

NIVEL_ORDEN = ["Bajo", "Medio", "Alto"]
ALPHA = 0.05
N_BOOTSTRAP = 10_000
BOOTSTRAP_SEED = 2225437


def bootstrap_median_ci(
    values: np.ndarray,
    n_boot: int = N_BOOTSTRAP,
    alpha: float = ALPHA,
    seed: int = BOOTSTRAP_SEED,
) -> tuple[float, float, float, float]:
    """Calcula la mediana bootstrap, el error estándar bootstrap y el IC (1-alpha) por percentiles."""
    rng = np.random.default_rng(seed)
    n = len(values)
    samples = rng.choice(values, size=(n_boot, n), replace=True)
    boot_medians = np.median(samples, axis=1)
    boot_med = float(np.median(boot_medians))
    boot_se = float(np.std(boot_medians, ddof=1))
    ci_low = float(np.percentile(boot_medians, 100 * (alpha / 2.0)))
    ci_high = float(np.percentile(boot_medians, 100 * (1.0 - alpha / 2.0)))
    return boot_med, ci_low, ci_high, boot_se


def run_analysis(raw_csv: Path | None = None) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Ejecuta ANOVA de dos factores y análisis Bootstrap sobre los resultados experimentales."""
    if raw_csv is None:
        raw_csv = RESULTS_DIR / "raw_runs.csv"

    df = pd.read_csv(raw_csv)
    df["nivel_temperatura"] = pd.Categorical(
        df["nivel_temperatura"], categories=NIVEL_ORDEN, ordered=True
    )
    df["tamano"] = df["tamano"].astype(int)

    # 1. ANOVA de dos factores (exactamente como especifican las instrucciones)
    modelo = ols("costo ~ C(temperatura) * C(tamano)", data=df).fit()
    tabla_anova = sm.stats.anova_lm(modelo, typ=2)
    tabla_anova["significativo_0.05"] = tabla_anova["PR(>F)"] < ALPHA

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    anova_out = tabla_anova.copy()
    anova_out.index.name = "fuente"
    anova_out.to_csv(RESULTS_DIR / "anova_table.csv")

    print("\n=== TABLA ANOVA DE DOS FACTORES (alpha = 0.05) ===")
    print(tabla_anova.to_string())

    # Verificar significancia de efectos
    sig_temp = bool(tabla_anova.loc["C(temperatura)", "PR(>F)"] < ALPHA)
    sig_tam = bool(tabla_anova.loc["C(tamano)", "PR(>F)"] < ALPHA)
    sig_int = bool(tabla_anova.loc["C(temperatura):C(tamano)", "PR(>F)"] < ALPHA)
    print(
        f"\nEfectos significativos (p < {ALPHA}): "
        f"Temperatura={sig_temp}, Tamano={sig_tam}, Interaccion={sig_int}"
    )

    # 2. Bootstrap para cada punto de diseño
    design_rows = []
    for idx_n, n in enumerate(sorted(df["tamano"].unique())):
        for idx_l, nivel in enumerate(NIVEL_ORDEN):
            sub = df[(df["tamano"] == n) & (df["nivel_temperatura"] == nivel)]
            if sub.empty:
                continue
            vals = sub["costo"].to_numpy(dtype=float)
            temp_val = float(sub["temperatura"].iloc[0])
            frac_val = float(sub["fraccion"].iloc[0])

            boot_med, ci_low, ci_high, boot_se = bootstrap_median_ci(
                vals,
                n_boot=N_BOOTSTRAP,
                alpha=ALPHA,
                seed=BOOTSTRAP_SEED + 100 * idx_n + idx_l,
            )
            design_rows.append(
                {
                    "tamano": int(n),
                    "nivel_temperatura": nivel,
                    "fraccion": frac_val,
                    "T0": temp_val,
                    "n_replicas": len(vals),
                    "media_muestral": float(np.mean(vals)),
                    "std_muestral": float(np.std(vals, ddof=1)),
                    "min_muestral": float(np.min(vals)),
                    "max_muestral": float(np.max(vals)),
                    "mediana_muestral": float(np.median(vals)),
                    "mediana_bootstrap": boot_med,
                    "ic_95_inf": ci_low,
                    "ic_95_sup": ci_high,
                    "se_bootstrap": boot_se,
                    "ic_ancho": ci_high - ci_low,
                    "efecto_significativo": sig_temp or sig_tam or sig_int,
                }
            )

    boot_df = pd.DataFrame(design_rows)
    boot_df.to_csv(RESULTS_DIR / "bootstrap_design_points.csv", index=False)

    print("\n=== RESUMEN BOOTSTRAP POR PUNTO DE DISEÑO (B = 10,000, IC 95%) ===")
    print(
        boot_df[
            [
                "tamano",
                "nivel_temperatura",
                "T0",
                "media_muestral",
                "std_muestral",
                "mediana_bootstrap",
                "ic_95_inf",
                "ic_95_sup",
            ]
        ].to_string(index=False)
    )

    # 3. Tabla resumen óptima por tamaño (n = 5, 10, 15)
    # Criterio primario: menor mediana bootstrap; desempate: menor media muestral, luego menor límite superior IC
    opt_rows = []
    for n in sorted(boot_df["tamano"].unique()):
        sub_n = boot_df[boot_df["tamano"] == n].copy()
        sub_n["_med_r"] = sub_n["mediana_bootstrap"].round(6)
        sub_n["_mean_r"] = sub_n["media_muestral"].round(6)
        sub_n["_sup_r"] = sub_n["ic_95_sup"].round(6)
        sub_n["_std_r"] = sub_n["std_muestral"].round(6)
        sub_n = sub_n.sort_values(
            by=["_med_r", "_mean_r", "_sup_r", "_std_r", "T0"],
            ascending=[True, True, True, True, True],
        )
        best = sub_n.iloc[0]
        opt_rows.append(
            {
                "tamano": int(best["tamano"]),
                "nivel_optimo": str(best["nivel_temperatura"]),
                "T_optima": float(best["T0"]),
                "mediana_bootstrap": float(best["mediana_bootstrap"]),
                "ic_95_inf": float(best["ic_95_inf"]),
                "ic_95_sup": float(best["ic_95_sup"]),
                "media_muestral": float(best["media_muestral"]),
                "std_muestral": float(best["std_muestral"]),
            }
        )

    opt_df = pd.DataFrame(opt_rows)
    opt_df.to_csv(RESULTS_DIR / "optimal_parameters_summary.csv", index=False)

    print("\n=== TABLA RESUMEN: PARÁMETRO ÓPTIMO POR TAMAÑO DE PROBLEMA ===")
    print(opt_df.to_string(index=False))

    return tabla_anova, boot_df, opt_df


if __name__ == "__main__":
    run_analysis()
