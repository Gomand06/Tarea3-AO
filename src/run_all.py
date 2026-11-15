"""
Script principal para reproducir de principio a fin la Tarea 3 (DOE - Opción A):
1. Genera/carga instancias fijas TSP para n in {5, 10, 15}.
2. Ejecuta las 90 corridas del Diseño Factorial Completo 3×3.
3. Calcula el ANOVA de dos factores y las estimaciones Bootstrap (B = 10,000).
4. Genera las gráficas de efectos principales, interacción e intervalos bootstrap.
"""

from __future__ import annotations

from build_pdf_report import build_pdf
from doe_experiment import run_experiment
from plots import generate_all_plots
from stats_analysis import run_analysis
from tsp_sa import generar_y_guardar_instancias


def main() -> None:
    print("=" * 70)
    print("PASO 1: Generación de instancias fijas TSP (n = 5, 10, 15)")
    print("=" * 70)
    insts = generar_y_guardar_instancias()
    for n, info in insts.items():
        print(f"  n={n:2d} -> óptimo exacto Held-Karp = {info['costo_optimo_exacto']:.4f}")

    print("\n" + "=" * 70)
    print("PASO 2: Ejecución del Diseño Factorial Completo 3×3 (90 corridas)")
    print("=" * 70)
    run_experiment()

    print("\n" + "=" * 70)
    print("PASO 3: Análisis Estadístico (ANOVA de 2 factores y Bootstrap)")
    print("=" * 70)
    run_analysis()

    print("\n" + "=" * 70)
    print("PASO 4: Generación de Gráficas")
    print("=" * 70)
    generate_all_plots()

    print("\n" + "=" * 70)
    print("PASO 5: Generación de Reporte PDF")
    print("=" * 70)
    pdf_path = build_pdf()
    print(f"Reporte PDF generado en {pdf_path}")


if __name__ == "__main__":
    main()
