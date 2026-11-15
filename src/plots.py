"""
Generación de gráficas para la Tarea 3 (DOE - Opción A):
1. Gráfica de efectos principales (Temperatura y Tamaño n).
2. Gráfica de interacción (Temperatura x Tamaño n) en escala absoluta y normalizada.
3. Gráfica de medianas bootstrap e intervalos de confianza del 95% por cada tamaño n.

Exporta cada figura en formato PDF (vectorial para LaTeX) y PNG (para GitHub README)
tanto en figures/ como en report/figures/ (listo para Overleaf).
"""

from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", os.path.join(os.environ.get("TEMP", "."), "mplconfig"))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

ROOT_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = ROOT_DIR / "results"
FIGURES_DIR = ROOT_DIR / "figures"
REPORT_FIGURES_DIR = ROOT_DIR / "report" / "figures"

NIVEL_ORDEN = ["Bajo", "Medio", "Alto"]
PALETTE_TAMANO = {5: "#1f77b4", 10: "#ff7f0e", 15: "#2ca02c"}


def _configure_style() -> None:
    sns.set_theme(style="whitegrid", context="paper")
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "axes.titlesize": 11,
            "axes.titleweight": "bold",
            "axes.labelsize": 10,
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
            "legend.fontsize": 9,
            "figure.dpi": 150,
            "savefig.bbox": "tight",
        }
    )


def _save_figure(fig: plt.Figure, stem: str) -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    for out_dir in (FIGURES_DIR, REPORT_FIGURES_DIR):
        fig.savefig(out_dir / f"{stem}.pdf", format="pdf")
        fig.savefig(out_dir / f"{stem}.png", format="png", dpi=300)
    plt.close(fig)


def _bootstrap_ci_array(values: np.ndarray, n_boot: int = 5000, seed: int = 2225437) -> tuple[float, float, float]:
    rng = np.random.default_rng(seed)
    samples = rng.choice(values, size=(n_boot, len(values)), replace=True)
    meds = np.median(samples, axis=1)
    means = np.mean(samples, axis=1)
    return (
        float(np.mean(means)),
        float(np.percentile(meds, 2.5)),
        float(np.percentile(meds, 97.5)),
    )


def plot_main_effects(raw_df: pd.DataFrame) -> None:
    """Genera la gráfica de efectos principales para Temperatura y Tamaño n."""
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.4))

    # Panel A: Efecto principal de Temperatura
    ax = axes[0]
    temp_labels = []
    temp_means = []
    temp_medians = []
    temp_ci_low = []
    temp_ci_high = []
    for idx, lvl in enumerate(NIVEL_ORDEN):
        sub = raw_df[raw_df["nivel_temperatura"] == lvl]
        vals = sub["costo"].to_numpy(dtype=float)
        t_val = float(sub["temperatura"].iloc[0])
        temp_labels.append(f"{lvl}\n($T_0={t_val:.2f}$)")
        temp_means.append(float(np.mean(vals)))
        med = float(np.median(vals))
        temp_medians.append(med)
        _, lo, hi = _bootstrap_ci_array(vals, seed=1000 + idx)
        temp_ci_low.append(max(0.0, med - lo))
        temp_ci_high.append(max(0.0, hi - med))

    x_pos = np.arange(len(NIVEL_ORDEN))
    ax.plot(x_pos, temp_means, marker="o", lw=2.2, color="#1b4f72", label="Media muestral")
    ax.errorbar(
        x_pos,
        temp_medians,
        yerr=[temp_ci_low, temp_ci_high],
        fmt="s--",
        lw=1.8,
        capsize=5,
        color="#d35400",
        label="Mediana (IC 95% bootstrap)",
    )
    for x, m in zip(x_pos, temp_means):
        ax.annotate(f"{m:.1f}", (x, m), textcoords="offset points", xytext=(0, 8), ha="center", fontsize=8.5, color="#1b4f72")
    ax.set_xticks(x_pos)
    ax.set_xticklabels(temp_labels)
    ax.set_xlabel("Nivel de Temperatura Inicial ($T_0$)")
    ax.set_ylabel("Costo del Tour TSP")
    ax.set_title("Efecto Principal: Temperatura")
    ax.legend(loc="best", frameon=True)

    # Panel B: Efecto principal de Tamaño (Bloque)
    ax = axes[1]
    sizes = sorted(raw_df["tamano"].unique())
    size_means = []
    size_medians = []
    size_ci_low = []
    size_ci_high = []
    for idx, n in enumerate(sizes):
        vals = raw_df[raw_df["tamano"] == n]["costo"].to_numpy(dtype=float)
        size_means.append(float(np.mean(vals)))
        med = float(np.median(vals))
        size_medians.append(med)
        _, lo, hi = _bootstrap_ci_array(vals, seed=2000 + idx)
        size_ci_low.append(max(0.0, med - lo))
        size_ci_high.append(max(0.0, hi - med))

    x_s = np.arange(len(sizes))
    ax.plot(x_s, size_means, marker="o", lw=2.2, color="#1b4f72", label="Media muestral")
    ax.errorbar(
        x_s,
        size_medians,
        yerr=[size_ci_low, size_ci_high],
        fmt="s--",
        lw=1.8,
        capsize=5,
        color="#d35400",
        label="Mediana (IC 95% bootstrap)",
    )
    for x, m in zip(x_s, size_means):
        ax.annotate(f"{m:.1f}", (x, m), textcoords="offset points", xytext=(0, 8), ha="center", fontsize=8.5, color="#1b4f72")
    ax.set_xticks(x_s)
    ax.set_xticklabels([f"n = {n}" for n in sizes])
    ax.set_xlabel("Tamaño del Problema TSP (n)")
    ax.set_ylabel("Costo del Tour TSP")
    ax.set_title("Efecto Principal: Tamaño del Problema (n)")
    ax.legend(loc="best", frameon=True)

    fig.suptitle("Análisis de Efectos Principales — Diseño Factorial Completo 3×3", fontsize=12.5, fontweight="bold", y=1.02)
    fig.tight_layout()
    _save_figure(fig, "main_effects")


def plot_interaction(boot_df: pd.DataFrame) -> None:
    """Genera la gráfica de interacción Temperatura × Tamaño (escala absoluta y normalizada)."""
    fig, axes = plt.subplots(1, 2, figsize=(11.6, 4.6))
    x_pos = np.arange(len(NIVEL_ORDEN))

    t_map = {}
    for lvl in NIVEL_ORDEN:
        t_map[lvl] = float(boot_df[boot_df["nivel_temperatura"] == lvl]["T0"].iloc[0])
    x_labels = [f"{lvl}\n($T_0={t_map[lvl]:.2f}$)" for lvl in NIVEL_ORDEN]

    # Panel 1: Escala absoluta (Mediana Bootstrap + IC 95%)
    ax = axes[0]
    for n in sorted(boot_df["tamano"].unique()):
        sub = boot_df[boot_df["tamano"] == n].set_index("nivel_temperatura").loc[NIVEL_ORDEN]
        y = sub["mediana_bootstrap"].to_numpy()
        yerr_low = np.maximum(0.0, y - sub["ic_95_inf"].to_numpy())
        yerr_high = np.maximum(0.0, sub["ic_95_sup"].to_numpy() - y)
        ax.errorbar(
            x_pos,
            y,
            yerr=[yerr_low, yerr_high],
            marker="o",
            lw=2.1,
            capsize=4,
            color=PALETTE_TAMANO[n],
            label=f"n = {n}",
        )
    ax.set_xticks(x_pos)
    ax.set_xticklabels(x_labels)
    ax.set_xlabel("Nivel de Temperatura ($T_0$)")
    ax.set_ylabel("Mediana Bootstrap del Costo (IC 95%)")
    ax.set_title("Interacción Temperatura × Tamaño (Escala Absoluta)")
    ax.legend(title="Bloque (n)", frameon=True)

    # Panel 2: Costo relativo (%) respecto al mínimo de cada tamaño (para ver cruce de pendientes)
    ax = axes[1]
    for n in sorted(boot_df["tamano"].unique()):
        sub = boot_df[boot_df["tamano"] == n].set_index("nivel_temperatura").loc[NIVEL_ORDEN]
        meds = sub["mediana_bootstrap"].to_numpy()
        means = sub["media_muestral"].to_numpy()
        ref = np.min(meds)
        rel_med = 100.0 * (meds - ref) / ref
        rel_mean = 100.0 * (means - np.min(means)) / np.min(means)
        ax.plot(
            x_pos,
            rel_med,
            marker="o",
            lw=2.2,
            color=PALETTE_TAMANO[n],
            label=f"n = {n} (mediana)",
        )
        ax.plot(
            x_pos,
            rel_mean,
            marker="x",
            ls=":",
            lw=1.5,
            alpha=0.75,
            color=PALETTE_TAMANO[n],
            label=f"n = {n} (media)",
        )
    ax.axhline(0.0, color="gray", lw=0.9, ls="--")
    ax.set_xticks(x_pos)
    ax.set_xticklabels(x_labels)
    ax.set_xlabel("Nivel de Temperatura ($T_0$)")
    ax.set_ylabel("Incremento Porcentual sobre el Óptimo de su Bloque (%)")
    ax.set_title("Interacción Relativa (Cruce de Pendientes entre Bloques)")
    ax.legend(ncol=2, fontsize=8, frameon=True)

    fig.suptitle("Gráfica de Interacción: Temperatura × Tamaño del Problema TSP", fontsize=12.5, fontweight="bold", y=1.02)
    fig.tight_layout()
    _save_figure(fig, "interaction")


def plot_bootstrap_intervals(raw_df: pd.DataFrame, boot_df: pd.DataFrame, opt_df: pd.DataFrame) -> None:
    """Genera 3 subgráficas (n = 5, 10, 15) con réplicas, mediana bootstrap e IC 95%."""
    sizes = sorted(boot_df["tamano"].unique())
    fig, axes = plt.subplots(1, len(sizes), figsize=(12.6, 4.4))

    for ax, n in zip(axes, sizes):
        sub_boot = boot_df[boot_df["tamano"] == n].set_index("nivel_temperatura").loc[NIVEL_ORDEN]
        sub_raw = raw_df[raw_df["tamano"] == n]
        opt_nivel = str(opt_df[opt_df["tamano"] == n]["nivel_optimo"].iloc[0])

        x_pos = np.arange(len(NIVEL_ORDEN))
        # Boxplot tenue o dispersión de las 10 réplicas
        for idx, lvl in enumerate(NIVEL_ORDEN):
            pts = sub_raw[sub_raw["nivel_temperatura"] == lvl]["costo"].to_numpy()
            jitter = np.linspace(-0.12, 0.12, len(pts))
            ax.scatter(
                np.full_like(pts, idx, dtype=float) + jitter,
                pts,
                s=22,
                alpha=0.45,
                color="#5d6d7e",
                zorder=2,
            )

        # Barras de error IC 95% Bootstrap y destaque del nivel óptimo
        for idx, lvl in enumerate(NIVEL_ORDEN):
            row = sub_boot.loc[lvl]
            med = float(row["mediana_bootstrap"])
            lo = float(row["ic_95_inf"])
            hi = float(row["ic_95_sup"])
            is_opt = lvl == opt_nivel
            color = "#1e8449" if is_opt else "#2874a6"
            marker = "D" if is_opt else "o"
            ms = 7.5 if is_opt else 6.0
            ax.errorbar(
                idx,
                med,
                yerr=[[max(0.0, med - lo)], [max(0.0, hi - med)]],
                fmt=marker,
                markersize=ms,
                color=color,
                ecolor=color,
                elinewidth=2.2,
                capsize=6,
                zorder=4,
                label="Óptimo $T^*$" if is_opt else ("Otro nivel" if idx == (0 if opt_nivel != "Bajo" else 1) else None),
            )
            ax.annotate(
                f"{med:.1f}",
                (idx, hi),
                textcoords="offset points",
                xytext=(0, 6),
                ha="center",
                fontsize=8.5,
                fontweight="bold" if is_opt else "normal",
                color=color,
            )

        # Margen vertical superior para que las etiquetas y leyendas no se encimen
        all_pts = sub_raw["costo"].to_numpy()
        y_min, y_max = float(np.min(all_pts)), float(np.max(all_pts))
        span = max(1.0, y_max - y_min)
        ax.set_ylim(y_min - 0.08 * span, y_max + 0.24 * span)

        t_labels = [f"{lvl}\n({sub_boot.loc[lvl, 'T0']:.1f})" for lvl in NIVEL_ORDEN]
        ax.set_xticks(x_pos)
        ax.set_xticklabels(t_labels)
        ax.set_xlabel("Nivel ($T_0$)")
        ax.set_title(f"Tamaño n = {n} (Óptimo: {opt_nivel})")
        if ax is axes[0]:
            ax.set_ylabel("Costo del Tour TSP")
        ax.legend(loc="upper left" if n == 5 else "best", fontsize=8, frameon=True)

    fig.suptitle("Mediana Bootstrap (B = 10,000) e IC del 95% por Punto de Diseño", fontsize=12.5, fontweight="bold", y=1.02)
    fig.tight_layout()
    _save_figure(fig, "bootstrap_intervals")


def generate_all_plots() -> None:
    """Carga los CSV de resultados y genera todas las gráficas del estudio."""
    _configure_style()
    raw_df = pd.read_csv(RESULTS_DIR / "raw_runs.csv")
    boot_df = pd.read_csv(RESULTS_DIR / "bootstrap_design_points.csv")
    opt_df = pd.read_csv(RESULTS_DIR / "optimal_parameters_summary.csv")

    plot_main_effects(raw_df)
    plot_interaction(boot_df)
    plot_bootstrap_intervals(raw_df, boot_df, opt_df)
    print(f"Gráficas generadas exitosamente en {FIGURES_DIR} y {REPORT_FIGURES_DIR}")


if __name__ == "__main__":
    generate_all_plots()
