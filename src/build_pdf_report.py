"""
Generación del reporte académico en PDF (report/reporte_tarea3.pdf) con portada
institucional, paleta Rojo con Café y los datos/gráficas reales del experimento
DOE de AO (Opción A).
"""

from __future__ import annotations

import json
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", os.path.join(os.environ.get("TEMP", "."), "mplconfig"))

import matplotlib
import pandas as pd
from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    HRFlowable,
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
RESULTS_DIR = ROOT_DIR / "results"
FIGURES_DIR = ROOT_DIR / "figures"
REPORT_DIR = ROOT_DIR / "report"
PDF_PATH = REPORT_DIR / "reporte_tarea3.pdf"

REPO_URL = "https://github.com/Gomand06/Tarea3-AO"
AUTOR = "Christopher Gómez Andrade"
MATRICULA = "2225437"
FACULTAD = "Facultad de Ciencias Físico Matemáticas"
CARRERA = "Carrera de Licenciatura en Ciencias Computacionales"
TITULO_TRABAJO = "DOE de AO"

# Paleta Rojo con Café
COLOR_ROJO = colors.HexColor("#8B1E1E")
COLOR_ROJO_SUAVE = colors.HexColor("#F9EBEA")
COLOR_CAFE = colors.HexColor("#5C3A21")
COLOR_CAFE_CLARO = colors.HexColor("#8B5A2B")
COLOR_CREMA = colors.HexColor("#FDF8F5")
COLOR_CREMA_BORDE = colors.HexColor("#D7C4BA")
COLOR_TEXTO = colors.HexColor("#2B1D16")
COLOR_MUTED = colors.HexColor("#7B5E50")


def _register_fonts() -> None:
    """Registra fuentes TrueType DejaVu para soporte completo Unicode y matemático."""
    ttf_dir = Path(matplotlib.get_data_path()) / "fonts" / "ttf"
    pdfmetrics.registerFont(TTFont("DejaVu", str(ttf_dir / "DejaVuSans.ttf")))
    pdfmetrics.registerFont(TTFont("DejaVu-Bold", str(ttf_dir / "DejaVuSans-Bold.ttf")))
    pdfmetrics.registerFont(TTFont("DejaVu-Oblique", str(ttf_dir / "DejaVuSans-Oblique.ttf")))
    pdfmetrics.registerFont(TTFont("DejaVu-BoldOblique", str(ttf_dir / "DejaVuSans-BoldOblique.ttf")))
    pdfmetrics.registerFont(TTFont("DejaVuMono", str(ttf_dir / "DejaVuSansMono.ttf")))
    registerFontFamily(
        "DejaVu",
        normal="DejaVu",
        bold="DejaVu-Bold",
        italic="DejaVu-Oblique",
        boldItalic="DejaVu-BoldOblique",
    )


def _build_styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "cover_facultad": ParagraphStyle(
            "CoverFacultad",
            parent=base["Normal"],
            fontName="DejaVu-Bold",
            fontSize=15,
            leading=20,
            textColor=COLOR_CAFE,
            alignment=TA_CENTER,
            spaceAfter=4,
        ),
        "cover_carrera": ParagraphStyle(
            "CoverCarrera",
            parent=base["Normal"],
            fontName="DejaVu-Bold",
            fontSize=12,
            leading=16,
            textColor=COLOR_ROJO,
            alignment=TA_CENTER,
            spaceAfter=18,
        ),
        "cover_title": ParagraphStyle(
            "CoverTitle",
            parent=base["Title"],
            fontName="DejaVu-Bold",
            fontSize=28,
            leading=34,
            textColor=COLOR_ROJO,
            alignment=TA_CENTER,
            spaceAfter=10,
        ),
        "cover_subtitle": ParagraphStyle(
            "CoverSubtitle",
            parent=base["Normal"],
            fontName="DejaVu",
            fontSize=11.5,
            leading=16.5,
            textColor=COLOR_CAFE,
            alignment=TA_CENTER,
            spaceAfter=8,
        ),
        "cover_meta": ParagraphStyle(
            "CoverMeta",
            parent=base["Normal"],
            fontName="DejaVu",
            fontSize=10.8,
            leading=16,
            textColor=COLOR_TEXTO,
            alignment=TA_CENTER,
        ),
        "h1": ParagraphStyle(
            "H1Custom",
            parent=base["Heading1"],
            fontName="DejaVu-Bold",
            fontSize=12,
            leading=15,
            textColor=COLOR_ROJO,
            spaceBefore=11,
            spaceAfter=5,
            keepWithNext=True,
        ),
        "h2": ParagraphStyle(
            "H2Custom",
            parent=base["Heading2"],
            fontName="DejaVu-Bold",
            fontSize=10.2,
            leading=13.5,
            textColor=COLOR_CAFE,
            spaceBefore=8,
            spaceAfter=3,
            keepWithNext=True,
        ),
        "body": ParagraphStyle(
            "BodyCustom",
            parent=base["Normal"],
            fontName="DejaVu",
            fontSize=9.2,
            leading=13.2,
            textColor=COLOR_TEXTO,
            alignment=TA_JUSTIFY,
            spaceAfter=5,
        ),
        "bullet": ParagraphStyle(
            "BulletCustom",
            parent=base["Normal"],
            fontName="DejaVu",
            fontSize=9.0,
            leading=12.8,
            textColor=COLOR_TEXTO,
            alignment=TA_JUSTIFY,
            leftIndent=14,
            firstLineIndent=-9,
            spaceAfter=3.8,
        ),
        "abstract": ParagraphStyle(
            "AbstractCustom",
            parent=base["Normal"],
            fontName="DejaVu",
            fontSize=8.9,
            leading=12.6,
            textColor=COLOR_TEXTO,
            alignment=TA_JUSTIFY,
        ),
        "caption": ParagraphStyle(
            "CaptionCustom",
            parent=base["Normal"],
            fontName="DejaVu-Oblique",
            fontSize=8.3,
            leading=11.2,
            textColor=COLOR_MUTED,
            alignment=TA_CENTER,
            spaceBefore=3,
            spaceAfter=8,
        ),
        "table_title": ParagraphStyle(
            "TableTitleCustom",
            parent=base["Normal"],
            fontName="DejaVu-Bold",
            fontSize=8.8,
            leading=11.5,
            textColor=COLOR_CAFE,
            alignment=TA_LEFT,
            spaceBefore=6,
            spaceAfter=3,
            keepWithNext=True,
        ),
        "cell": ParagraphStyle(
            "CellCustom",
            parent=base["Normal"],
            fontName="DejaVu",
            fontSize=8.2,
            leading=10.5,
            textColor=COLOR_TEXTO,
            alignment=TA_CENTER,
        ),
        "cell_left": ParagraphStyle(
            "CellLeftCustom",
            parent=base["Normal"],
            fontName="DejaVu",
            fontSize=8.2,
            leading=10.5,
            textColor=COLOR_TEXTO,
            alignment=TA_LEFT,
        ),
        "cell_header": ParagraphStyle(
            "CellHeaderCustom",
            parent=base["Normal"],
            fontName="DejaVu-Bold",
            fontSize=8.2,
            leading=10.5,
            textColor=colors.white,
            alignment=TA_CENTER,
        ),
    }


def _scaled_image(path: Path, max_width: float, max_height: float | None = None) -> Image:
    """Crea un objeto Image preservando exactamente la relación de aspecto original."""
    with PILImage.open(path) as im:
        w_px, h_px = im.size
    aspect = h_px / w_px
    width = max_width
    height = width * aspect
    if max_height is not None and height > max_height:
        height = max_height
        width = height / aspect
    img = Image(str(path), width=width, height=height)
    img.hAlign = "CENTER"
    return img


def _styled_table(
    data: list[list],
    col_widths: list[float],
    highlight_rows: list[int] | None = None,
) -> Table:
    tbl = Table(data, colWidths=col_widths, repeatRows=1)
    style_cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), COLOR_ROJO),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("LINEABOVE", (0, 0), (-1, 0), 1.2, COLOR_CAFE),
        ("LINEBELOW", (0, 0), (-1, 0), 1.2, COLOR_CAFE),
        ("LINEBELOW", (0, -1), (-1, -1), 1.2, COLOR_CAFE),
        ("GRID", (0, 1), (-1, -1), 0.35, COLOR_CREMA_BORDE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, COLOR_CREMA]),
    ]
    if highlight_rows:
        for r_idx in highlight_rows:
            style_cmds.append(("BACKGROUND", (0, r_idx), (-1, r_idx), COLOR_ROJO_SUAVE))
    tbl.setStyle(TableStyle(style_cmds))
    return tbl


def _draw_cover_frame(canvas, doc) -> None:
    """Marco decorativo Rojo con Café para la portada (sin encabezado ni número de página)."""
    canvas.saveState()
    page_w, page_h = letter
    canvas.setFillColor(COLOR_ROJO)
    canvas.rect(doc.leftMargin, page_h - 1.3 * cm, page_w - doc.leftMargin - doc.rightMargin, 0.22 * cm, fill=1, stroke=0)
    canvas.setFillColor(COLOR_CAFE)
    canvas.rect(doc.leftMargin, page_h - 1.62 * cm, page_w - doc.leftMargin - doc.rightMargin, 0.09 * cm, fill=1, stroke=0)

    canvas.setFillColor(COLOR_CAFE)
    canvas.rect(doc.leftMargin, 1.3 * cm, page_w - doc.leftMargin - doc.rightMargin, 0.09 * cm, fill=1, stroke=0)
    canvas.setFillColor(COLOR_ROJO)
    canvas.rect(doc.leftMargin, 1.0 * cm, page_w - doc.leftMargin - doc.rightMargin, 0.22 * cm, fill=1, stroke=0)
    canvas.restoreState()


def _draw_page_chrome(canvas, doc) -> None:
    """Encabezado y pie de página en Rojo con Café a partir de la página 2."""
    canvas.saveState()
    page_w, page_h = letter
    canvas.setFont("DejaVu-Bold", 7.8)
    canvas.setFillColor(COLOR_ROJO)
    canvas.drawString(doc.leftMargin, page_h - 1.18 * cm, f"{TITULO_TRABAJO} — {FACULTAD}")
    canvas.setFont("DejaVu", 7.8)
    canvas.setFillColor(COLOR_CAFE)
    canvas.drawRightString(page_w - doc.rightMargin, page_h - 1.18 * cm, f"{AUTOR} | {MATRICULA}")

    canvas.setStrokeColor(COLOR_ROJO)
    canvas.setLineWidth(0.75)
    canvas.line(doc.leftMargin, page_h - 1.35 * cm, page_w - doc.rightMargin, page_h - 1.35 * cm)
    canvas.setStrokeColor(COLOR_CAFE_CLARO)
    canvas.setLineWidth(0.6)
    canvas.line(doc.leftMargin, 1.35 * cm, page_w - doc.rightMargin, 1.35 * cm)

    canvas.setFillColor(COLOR_CAFE)
    canvas.setFont("DejaVu", 8.0)
    canvas.drawCentredString(page_w / 2.0, 0.9 * cm, f"Página {doc.page}")
    canvas.restoreState()


def build_pdf(output_path: Path = PDF_PATH) -> Path:
    """Construye el reporte en PDF con portada institucional, colores Rojo/Café y análisis completo."""
    _register_fonts()
    styles = _build_styles()

    with open(RESULTS_DIR / "experiment_config.json", "r", encoding="utf-8") as f:
        config = json.load(f)
    with open(DATA_DIR / "tsp_instances.json", "r", encoding="utf-8") as f:
        instances = json.load(f)

    anova_df = pd.read_csv(RESULTS_DIR / "anova_table.csv")
    boot_df = pd.read_csv(RESULTS_DIR / "bootstrap_design_points.csv")
    opt_df = pd.read_csv(RESULTS_DIR / "optimal_parameters_summary.csv")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        leftMargin=1.9 * cm,
        rightMargin=1.9 * cm,
        topMargin=2.0 * cm,
        bottomMargin=1.8 * cm,
        title=f"{TITULO_TRABAJO} - Tarea 3",
        author=AUTOR,
    )
    usable_w = letter[0] - doc.leftMargin - doc.rightMargin

    story = []

    # =========================================================================
    # PORTADA (Página 1)
    # =========================================================================
    story.append(Spacer(1, 0.9 * cm))
    logo_path = FIGURES_DIR / "uanl_logo.png"
    if logo_path.exists():
        story.append(_scaled_image(logo_path, max_width=11.5 * cm, max_height=5.6 * cm))
        story.append(Spacer(1, 0.8 * cm))

    story.append(Paragraph(FACULTAD, styles["cover_facultad"]))
    story.append(Paragraph(CARRERA, styles["cover_carrera"]))
    story.append(HRFlowable(width="55%", thickness=1.4, color=COLOR_CAFE, spaceBefore=4, spaceAfter=18))

    story.append(Paragraph(TITULO_TRABAJO, styles["cover_title"]))
    story.append(
        Paragraph(
            "<b>Tarea 3 — Ajuste de Parámetros con Diseño de Experimentos (DOE)</b><br/>"
            "Ajuste de la Temperatura Inicial T<sub>0</sub> en Recocido Simulado con 2-opt sobre TSP<br/>"
            "<i>Enfoque Seleccionado: Opción A — Diseño Factorial Completo 3×3</i>",
            styles["cover_subtitle"],
        )
    )
    story.append(Spacer(1, 1.3 * cm))

    cover_card = Table(
        [
            [
                Paragraph(
                    f"<b>Alumno:</b> {AUTOR}<br/>"
                    f"<b>Matrícula:</b> <font name='DejaVuMono'>{MATRICULA}</font><br/>"
                    f"<b>Carrera:</b> {CARRERA}<br/>"
                    f"<b>Facultad:</b> {FACULTAD}<br/>"
                    f"<b>Repositorio en GitHub:</b> "
                    f"<link href='{REPO_URL}' color='#8B1E1E'><u>{REPO_URL}</u></link>",
                    styles["cover_meta"],
                )
            ]
        ],
        colWidths=[usable_w * 0.88],
    )
    cover_card.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), COLOR_CREMA),
                ("BOX", (0, 0), (-1, -1), 1.0, COLOR_CAFE_CLARO),
                ("LINEBEFORE", (0, 0), (0, -1), 4.0, COLOR_ROJO),
                ("TOPPADDING", (0, 0), (-1, -1), 14),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
                ("LEFTPADDING", (0, 0), (-1, -1), 16),
                ("RIGHTPADDING", (0, 0), (-1, -1), 16),
            ]
        )
    )
    cover_card.hAlign = "CENTER"
    story.append(cover_card)
    story.append(Spacer(1, 1.8 * cm))
    story.append(
        Paragraph(
            "<font color='#5C3A21'><b>San Nicolás de los Garza, Nuevo León · Noviembre de 2026</b></font>",
            styles["cover_meta"],
        )
    )
    story.append(PageBreak())

    # =========================================================================
    # CONTENIDO PRINCIPAL (Página 2 en adelante)
    # =========================================================================
    r_val = float(config["r"])
    anova_map = {row["fuente"]: row for _, row in anova_df.iterrows()}
    p_temp = float(anova_map["C(temperatura)"]["PR(>F)"])
    f_temp = float(anova_map["C(temperatura)"]["F"])
    p_size = float(anova_map["C(tamano)"]["PR(>F)"])
    f_size = float(anova_map["C(tamano)"]["F"])
    p_int = float(anova_map["C(temperatura):C(tamano)"]["PR(>F)"])
    f_int = float(anova_map["C(temperatura):C(tamano)"]["F"])

    abs_box = Table(
        [
            [
                Paragraph(
                    "<b>Resumen Ejecutivo:</b> Se ajustó el parámetro de temperatura inicial <i>T<sub>0</sub></i> del "
                    "algoritmo de Recocido Simulado con operador 2-opt sobre instancias euclidianas del Problema del "
                    "Agente Viajero (TSP) mediante la <b>Opción A (Diseño Factorial Completo 3×3)</b>. Tomando como "
                    "factor la temperatura inicial (Bajo, Medio, Alto generados con la matrícula "
                    f"<font name='DejaVuMono'>{MATRICULA}</font>) y como bloque el tamaño <i>n</i> ∈ {{5, 10, 15}}, se "
                    "ejecutaron 10 réplicas independientes por punto de diseño (90 corridas en total). El ANOVA de dos "
                    f"factores (α = 0.05) demostró significancia estadística para la temperatura (<i>F</i> = {f_temp:.4f}, "
                    f"<i>p</i> = {p_temp:.6f}), el tamaño (<i>F</i> = {f_size:.2f}, <i>p</i> = {p_size:.2e}) y su "
                    f"interacción (<i>F</i> = {f_int:.4f}, <i>p</i> = {p_int:.6f}). Mediante remuestreo <i>bootstrap</i> "
                    "(<i>B</i> = 10,000, IC 95%) se concluyó que el mejor parámetro cambia conforme crece la instancia: "
                    "<b>Bajo (<i>T<sub>0</sub>*</i> = 32.9556)</b> para <i>n</i> = 5 y <b>Medio (<i>T<sub>0</sub>*</i> = 77.6556)</b> "
                    "para <i>n</i> = 10 y <i>n</i> = 15.<br/>"
                    f"<b>Repositorio público:</b> <link href='{REPO_URL}' color='#8B1E1E'><u>{REPO_URL}</u></link>",
                    styles["abstract"],
                )
            ]
        ],
        colWidths=[usable_w],
    )
    abs_box.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), COLOR_CREMA),
                ("LINEBEFORE", (0, 0), (0, -1), 3.5, COLOR_ROJO),
                ("BOX", (0, 0), (-1, -1), 0.5, COLOR_CREMA_BORDE),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ]
        )
    )
    story.append(abs_box)

    # Sección 1
    story.append(Paragraph("1. Diseño Experimental y Generación de Niveles de Temperatura", styles["h1"]))
    story.append(
        Paragraph(
            f"Siguiendo las especificaciones de la <b>Opción A (Diseño Factorial Completo)</b>, se evaluaron 3 niveles "
            f"de temperatura inicial <i>T<sub>0</sub></i> cruzados con 3 tamaños de instancia TSP (<i>n</i> ∈ {{5, 10, 15}}), "
            f"obteniendo 9 puntos de diseño. Con {config['n_replicas']} réplicas independientes de semillas distintas por "
            f"punto se completaron exactamente <b>{config['total_corridas']} corridas</b>.",
            styles["body"],
        )
    )
    story.append(
        Paragraph(
            f"Al inicio del experimento se fijó una única semilla aleatoria igual a la matrícula del estudiante "
            f"(<font name='DejaVuMono'>random.seed({MATRICULA}); r = random.random()</font>), obteniendo el valor fijo "
            f"<b><i>r</i> = {r_val:.16f}</b>. Se estableció el rango de temperatura inicial en "
            f"[<i>T<sub>mín</sub></i>, <i>T<sub>máx</sub></i>] = [{config['t_min']:.1f}, {config['t_max']:.1f}], "
            f"coherente con las barreras de energía Δ<i>E</i> de movimientos 2-opt en el plano [0, 1000]². Aplicando "
            f"<i>T<sub>nivel</sub></i> = <i>T<sub>mín</sub></i> + fracción · (<i>T<sub>máx</sub></i> − <i>T<sub>mín</sub></i>), "
            f"se obtuvieron los tres niveles detallados en la Tabla 1.",
            styles["body"],
        )
    )

    niveles_formula = {"Bajo": "0.3 · r", "Medio": "0.3 · r + 0.3", "Alto": "0.3 · r + 0.6"}
    t1_rows = [
        [
            Paragraph("Nivel", styles["cell_header"]),
            Paragraph("Fórmula de Fracción", styles["cell_header"]),
            Paragraph("Fracción Calculada", styles["cell_header"]),
            Paragraph("Temperatura Inicial T<sub>0</sub>", styles["cell_header"]),
        ]
    ]
    for lvl in config["niveles"]:
        t1_rows.append(
            [
                Paragraph(f"<b>{lvl['nivel']}</b>", styles["cell"]),
                Paragraph(niveles_formula[lvl["nivel"]], styles["cell"]),
                Paragraph(f"{lvl['fraccion']:.6f}", styles["cell"]),
                Paragraph(f"{lvl['temperatura']:.4f}", styles["cell"]),
            ]
        )
    story.append(
        KeepTogether(
            [
                Paragraph("Tabla 1. Niveles de temperatura inicial generados para la Opción A.", styles["table_title"]),
                _styled_table(t1_rows, [usable_w * 0.22, usable_w * 0.28, usable_w * 0.25, usable_w * 0.25]),
            ]
        )
    )

    # Sección 2
    story.append(Paragraph("2. Implementación del Recocido Simulado con 2-opt sobre TSP", styles["h1"]))
    story.append(
        Paragraph(
            "El algoritmo y el marco experimental se implementaron desde cero en Python "
            "(<font name='DejaVuMono'>src/tsp_sa.py</font> y <font name='DejaVuMono'>src/doe_experiment.py</font>):",
            styles["body"],
        )
    )
    opt_5 = instances["5"]["costo_optimo_exacto"]
    opt_10 = instances["10"]["costo_optimo_exacto"]
    opt_15 = instances["15"]["costo_optimo_exacto"]
    story.append(
        Paragraph(
            f"• <b>Instancias fijas por bloque:</b> Se generó una instancia euclidiana 2D fija en [0, 1000]² por cada "
            f"tamaño (<font name='DejaVuMono'>data/tsp_instances.json</font>, semillas 105, 110 y 115). Además, se "
            f"calculó el óptimo global exacto con programación dinámica Held-Karp como referencia: "
            f"<b>{opt_5:.4f}</b> (<i>n</i> = 5), <b>{opt_10:.4f}</b> (<i>n</i> = 10) y <b>{opt_15:.4f}</b> (<i>n</i> = 15).",
            styles["bullet"],
        )
    )
    story.append(
        Paragraph(
            "• <b>Operador de vecindario 2-opt:</b> En cada paso se eligen aleatoriamente dos índices <i>i</i> &lt; <i>j</i> "
            "y se evalúa en tiempo <i>O</i>(1) la variación de costo Δ<i>E</i> = (<i>d<sub>a,c</sub></i> + <i>d<sub>b,d</sub></i>) "
            "− (<i>d<sub>a,b</sub></i> + <i>d<sub>c,d</sub></i>) al invertir el subsegmento de ruta.",
            styles["bullet"],
        )
    )
    story.append(
        Paragraph(
            f"• <b>Criterio de Metropolis y enfriamiento:</b> Todo movimiento con Δ<i>E</i> ≤ 0 se acepta; los "
            f"deteriorantes (Δ<i>E</i> &gt; 0) se aceptan con probabilidad exp(−Δ<i>E</i> / <i>T</i>). La temperatura "
            f"desciende geométricamente <i>T<sub>k+1</sub></i> = α · <i>T<sub>k</sub></i> con α = {config['alpha']} "
            f"durante {config['epochs']} épocas de <i>n</i> evaluaciones cada una (presupuesto total 18<i>n</i> iteraciones), "
            f"registrando el costo del tour al final del enfriamiento.",
            styles["bullet"],
        )
    )

    # Sección 3
    story.append(Paragraph("3. Análisis de Varianza (ANOVA de Dos Factores)", styles["h1"]))
    story.append(
        Paragraph(
            "Se ajustó el modelo lineal con interacción <font name='DejaVuMono'>costo ~ C(temperatura) * C(tamano)</font> "
            "sobre las 90 corridas mediante <font name='DejaVuMono'>statsmodels</font> (ANOVA Tipo II, nivel de "
            "significancia α = 0.05). La Tabla 2 resume las cuatro fuentes de variación.",
            styles["body"],
        )
    )
    t2_rows = [
        [
            Paragraph("Fuente de Variación", styles["cell_header"]),
            Paragraph("Suma de Cuadrados", styles["cell_header"]),
            Paragraph("gl", styles["cell_header"]),
            Paragraph("Estadístico F", styles["cell_header"]),
            Paragraph("Valor p (PR(&gt;F))", styles["cell_header"]),
            Paragraph("¿Significativo?", styles["cell_header"]),
        ]
    ]
    label_map = {
        "C(temperatura)": "C(temperatura)",
        "C(tamano)": "C(tamano)",
        "C(temperatura):C(tamano)": "C(temperatura):C(tamano)",
        "Residual": "Residual (Error)",
    }
    for _, row in anova_df.iterrows():
        src = row["fuente"]
        if src == "Residual":
            f_str, p_str, sig_str = "—", "—", "—"
        else:
            f_str = f"{row['F']:.4f}"
            p_val = float(row["PR(>F)"])
            p_str = f"{p_val:.4e}" if p_val < 1e-3 else f"{p_val:.6f}"
            sig_str = "<b><font color='#8B1E1E'>Sí (p &lt; 0.05)</font></b>" if bool(row["significativo_0.05"]) else "No"
        t2_rows.append(
            [
                Paragraph(label_map.get(src, src), styles["cell_left"]),
                Paragraph(f"{row['sum_sq']:,.2f}", styles["cell"]),
                Paragraph(f"{int(row['df'])}", styles["cell"]),
                Paragraph(f_str, styles["cell"]),
                Paragraph(p_str, styles["cell"]),
                Paragraph(sig_str, styles["cell"]),
            ]
        )
    story.append(
        KeepTogether(
            [
                Paragraph("Tabla 2. Resultados del ANOVA de dos factores (α = 0.05, N = 90).", styles["table_title"]),
                _styled_table(
                    t2_rows,
                    [usable_w * 0.28, usable_w * 0.18, usable_w * 0.07, usable_w * 0.14, usable_w * 0.17, usable_w * 0.16],
                ),
            ]
        )
    )
    story.append(Spacer(1, 4))
    story.append(
        Paragraph(
            f"<b>Interpretación del ANOVA:</b> Los tres efectos evaluados resultaron estadísticamente significativos "
            f"(<i>p</i> &lt; 0.05): el tamaño del problema (<i>p</i> = {p_size:.2e}) domina la escala del costo, "
            f"el factor temperatura (<i>F</i> = {f_temp:.4f}, <i>p</i> = {p_temp:.6f}) altera significativamente el "
            f"desempeño del algoritmo, y la <b>interacción Temperatura × Tamaño (<i>F</i> = {f_int:.4f}, "
            f"<i>p</i> = {p_int:.6f})</b> demuestra que el efecto de <i>T<sub>0</sub></i> cambia según el tamaño "
            f"<i>n</i>. En consecuencia, procede estimar la mediana e IC del 95% vía <i>bootstrap</i> en todos los "
            f"puntos de diseño para seleccionar el parámetro óptimo de cada bloque.",
            styles["body"],
        )
    )

    # Sección 4: Gráficas
    story.append(Paragraph("4. Gráficas de Efectos Principales, Interacción y Bootstrap", styles["h1"]))
    story.append(
        KeepTogether(
            [
                _scaled_image(FIGURES_DIR / "main_effects.png", max_width=usable_w, max_height=7.0 * cm),
                Paragraph(
                    "Figura 1. Efectos principales de la temperatura inicial T<sub>0</sub> (izquierda) y del tamaño del "
                    "problema TSP n (derecha). En promedio global, el nivel Medio (77.66) obtiene el menor costo medio (2695.0).",
                    styles["caption"],
                ),
            ]
        )
    )
    story.append(
        KeepTogether(
            [
                _scaled_image(FIGURES_DIR / "interaction.png", max_width=usable_w, max_height=7.1 * cm),
                Paragraph(
                    "Figura 2. Gráfica de interacción Temperatura × Tamaño en escala absoluta (izquierda) y relativa "
                    "porcentual dentro de cada bloque (derecha). En n = 15 se observa una clara curva en «U» donde "
                    "T<sub>Bajo</sub> (+10.02%) y T<sub>Alto</sub> (+4.63%) empeoran frente a T<sub>Medio</sub>.",
                    styles["caption"],
                ),
            ]
        )
    )
    story.append(
        KeepTogether(
            [
                _scaled_image(FIGURES_DIR / "bootstrap_intervals.png", max_width=usable_w, max_height=7.0 * cm),
                Paragraph(
                    "Figura 3. Réplicas individuales, mediana bootstrap (B = 10,000) e intervalos de confianza del 95% "
                    "para cada punto de diseño. En rojo se destaca el nivel óptimo seleccionado por tamaño.",
                    styles["caption"],
                ),
            ]
        )
    )

    # Sección 5: Detalle Bootstrap
    story.append(Paragraph("5. Estimación Bootstrap por Punto de Diseño (B = 10,000, IC 95%)", styles["h1"]))
    story.append(
        Paragraph(
            "Para cada uno de los 9 puntos de diseño se realizaron <i>B</i> = 10,000 remuestreos <i>bootstrap</i> con "
            "reemplazo sobre sus 10 réplicas, calculando la mediana <i>bootstrap</i> y su intervalo de confianza al 95% "
            "(percentiles 2.5% y 97.5%). La Tabla 3 detalla los 9 puntos evaluados.",
            styles["body"],
        )
    )

    opt_lookup = {(int(r["tamano"]), str(r["nivel_optimo"])) for _, r in opt_df.iterrows()}
    t3_rows = [
        [
            Paragraph("n", styles["cell_header"]),
            Paragraph("Nivel", styles["cell_header"]),
            Paragraph("T<sub>0</sub>", styles["cell_header"]),
            Paragraph("Media", styles["cell_header"]),
            Paragraph("Desv. Est.", styles["cell_header"]),
            Paragraph("Mediana Boot.", styles["cell_header"]),
            Paragraph("IC 95% Inf.", styles["cell_header"]),
            Paragraph("IC 95% Sup.", styles["cell_header"]),
        ]
    ]
    highlight_t3 = []
    for idx, row in boot_df.iterrows():
        n_val = int(row["tamano"])
        lvl = str(row["nivel_temperatura"])
        is_opt = (n_val, lvl) in opt_lookup
        if is_opt:
            highlight_t3.append(idx + 1)
        lvl_txt = f"<b><font color='#8B1E1E'>{lvl} *</font></b>" if is_opt else lvl
        med_txt = f"<b><font color='#8B1E1E'>{row['mediana_bootstrap']:.2f}</font></b>" if is_opt else f"{row['mediana_bootstrap']:.2f}"
        t3_rows.append(
            [
                Paragraph(f"{n_val}", styles["cell"]),
                Paragraph(lvl_txt, styles["cell"]),
                Paragraph(f"{row['T0']:.2f}", styles["cell"]),
                Paragraph(f"{row['media_muestral']:.2f}", styles["cell"]),
                Paragraph(f"{row['std_muestral']:.2f}", styles["cell"]),
                Paragraph(med_txt, styles["cell"]),
                Paragraph(f"{row['ic_95_inf']:.2f}", styles["cell"]),
                Paragraph(f"{row['ic_95_sup']:.2f}", styles["cell"]),
            ]
        )
    story.append(
        KeepTogether(
            [
                Paragraph(
                    "Tabla 3. Estadísticos muestrales y estimaciones bootstrap (B = 10,000, IC 95%) por punto de diseño (* óptimo de su bloque).",
                    styles["table_title"],
                ),
                _styled_table(
                    t3_rows,
                    [
                        usable_w * 0.06,
                        usable_w * 0.13,
                        usable_w * 0.10,
                        usable_w * 0.13,
                        usable_w * 0.13,
                        usable_w * 0.15,
                        usable_w * 0.15,
                        usable_w * 0.15,
                    ],
                    highlight_rows=highlight_t3,
                ),
            ]
        )
    )

    # Sección 6: Entregable Final
    story.append(Paragraph("6. Entregable Final: Tabla Resumen y Análisis", styles["h1"]))

    t4_rows = [
        [
            Paragraph("Tamaño (n)", styles["cell_header"]),
            Paragraph("Óptimo Exacto", styles["cell_header"]),
            Paragraph("Nivel Óptimo", styles["cell_header"]),
            Paragraph("Temperatura T<sub>0</sub>*", styles["cell_header"]),
            Paragraph("Mediana Bootstrap", styles["cell_header"]),
            Paragraph("Intervalo de Confianza (95%)", styles["cell_header"]),
        ]
    ]
    for _, row in opt_df.iterrows():
        n_val = int(row["tamano"])
        exact_val = float(instances[str(n_val)]["costo_optimo_exacto"])
        t4_rows.append(
            [
                Paragraph(f"<b>{n_val}</b>", styles["cell"]),
                Paragraph(f"{exact_val:.4f}", styles["cell"]),
                Paragraph(f"<b><font color='#8B1E1E'>{row['nivel_optimo']}</font></b>", styles["cell"]),
                Paragraph(f"<b>{row['T_optima']:.4f}</b>", styles["cell"]),
                Paragraph(f"<b>{row['mediana_bootstrap']:.4f}</b>", styles["cell"]),
                Paragraph(f"[{row['ic_95_inf']:.4f}, {row['ic_95_sup']:.4f}]", styles["cell"]),
            ]
        )
    story.append(
        KeepTogether(
            [
                Paragraph("Tabla 4. Tabla resumen: temperatura óptima, mediana bootstrap e IC 95% para n = 5, 10, 15.", styles["table_title"]),
                _styled_table(
                    t4_rows,
                    [usable_w * 0.12, usable_w * 0.15, usable_w * 0.14, usable_w * 0.15, usable_w * 0.18, usable_w * 0.26],
                    highlight_rows=[1, 2, 3],
                ),
            ]
        )
    )

    story.append(Paragraph("6.1 Mejor parámetro encontrado por tamaño y cómo se llegó a esa conclusión", styles["h2"]))
    story.append(
        Paragraph(
            "El ANOVA de dos factores confirmó diferencias estadísticamente significativas debidas a la temperatura "
            f"(<i>F</i> = {f_temp:.4f}, <i>p</i> = {p_temp:.6f}) y a su interacción con el tamaño "
            f"(<i>F</i> = {f_int:.4f}, <i>p</i> = {p_int:.6f}), demostrando que la selección de <i>T<sub>0</sub>*</i> "
            "debe realizarse por tamaño mediante los intervalos de confianza <i>bootstrap</i>:",
            styles["body"],
        )
    )
    story.append(
        Paragraph(
            "• <b>Para <i>n</i> = 5 → Nivel Bajo (<i>T<sub>0</sub>*</i> = 32.9556):</b> Alcanzó la mediana del óptimo "
            "global exacto (<b>2313.4535</b>) con intervalo de confianza del 95% colapsado en "
            "<b>[2313.4535, 2313.4535]</b> (9 de 10 réplicas convergieron al óptimo) y la menor dispersión (media "
            "2314.39, DE 2.96). Subir <i>T<sub>0</sub></i> a Alto (122.36) empeoró la mediana a 2318.14 porque el "
            "sistema conserva agitación térmica residual al concluir las 18 épocas.",
            styles["bullet"],
        )
    )
    story.append(
        Paragraph(
            "• <b>Para <i>n</i> = 10 → Nivel Medio (<i>T<sub>0</sub>*</i> = 77.6556):</b> Los tres niveles empataron en "
            "mediana <i>bootstrap</i> exactamente en el óptimo global Held-Karp (<b>2676.4468</b>, IC 95% "
            "<b>[2676.4468, 2785.7350]</b>). Aplicando el criterio de desempate por menor costo promedio y menor "
            "variabilidad entre réplicas, se eligió el nivel <b>Medio</b> al presentar la menor media muestral "
            "(2722.74 frente a 2727.10 de Bajo) y menor desviación estándar (60.23 frente a 71.04 de Bajo).",
            styles["bullet"],
        )
    )
    story.append(
        Paragraph(
            "• <b>Para <i>n</i> = 15 → Nivel Medio (<i>T<sub>0</sub>*</i> = 77.6556):</b> Obtuvo el mejor desempeño "
            "categórico con mediana <i>bootstrap</i> de <b>3028.0827</b> (a solo 1.32% del óptimo exacto 2988.6778) e "
            "IC 95% estrecho de <b>[2988.6778, 3061.9949]</b>. Su intervalo de confianza es <b>completamente disjunto</b> "
            "respecto al nivel Bajo ([3129.7321, 3468.3587], mediana 3331.42), confirmando con más del 95% de confianza "
            "que Bajo queda atrapado por congelamiento prematuro. Además, Medio supera ampliamente en mediana y "
            "estabilidad a Alto (3168.24, IC [3045.1977, 3395.7156]).",
            styles["bullet"],
        )
    )

    story.append(Paragraph("6.2 ¿La temperatura óptima cambia con el tamaño del problema? ¿Hay una tendencia clara entre n y T*?", styles["h2"]))
    story.append(
        Paragraph(
            "<b>Sí, la temperatura óptima cambia con el tamaño del problema y existe una tendencia creciente de "
            "<i>T*</i> respecto a <i>n</i></b>, pasando de <b><i>T<sub>0</sub>*</i> = 32.9556 (Bajo)</b> en <i>n</i> = 5 "
            "a <b><i>T<sub>0</sub>*</i> = 77.6556 (Medio)</b> en <i>n</i> = 10 y <i>n</i> = 15. Físicamente, esta "
            "tendencia se explica por tres factores propios del algoritmo:",
            styles["body"],
        )
    )
    story.append(
        Paragraph(
            "1. <b>Expansión factorial del espacio de búsqueda:</b> El número de tours no dirigidos crece como "
            "(<i>n</i>−1)!/2: pasa de apenas <b>12</b> recorridos en <i>n</i> = 5 a <b>181,440</b> en <i>n</i> = 10 y "
            "<b>4.36 × 10¹⁰</b> en <i>n</i> = 15. En instancias muy pequeñas casi no hay mínimos locales profundos, por "
            "lo que una temperatura inicial baja acelera la convergencia sin ruido final.",
            styles["bullet"],
        )
    )
    story.append(
        Paragraph(
            "2. <b>Proliferación de mínimos locales 2-opt en instancias mayores:</b> Al alcanzar <i>n</i> = 15 surgen "
            "múltiples óptimos locales subóptimos. Con <i>T<sub>0</sub></i> = 32.96, Metropolis rechaza casi de inmediato "
            "movimientos deteriorantes (Δ<i>E</i> &gt; 0) y queda atrapado en recorridos ~10% más costosos; elevar "
            "<i>T<sub>0</sub></i> a 77.66 otorga la energía térmica necesaria para escapar de esas cuencas.",
            styles["bullet"],
        )
    )
    story.append(
        Paragraph(
            "3. <b>Equilibrio exploración–explotación bajo presupuesto finito:</b> Aunque <i>T*</i> aumenta con "
            "<i>n</i>, incrementarla en exceso al nivel Alto (122.36) con 18 épocas vuelve a degradar la solución en "
            "<i>n</i> = 15 (3168.24 frente a 3028.08) porque la cadena concluye demasiado caliente "
            "(<i>T<sub>f</sub></i> = 12.24) y no consolida el descenso final. Por ello, conforme aumenta <i>n</i>, la "
            "temperatura óptima evoluciona desde regímenes fríos de rápida explotación hacia valores intermedios balanceados.",
            styles["bullet"],
        )
    )

    doc.build(story, onFirstPage=_draw_cover_frame, onLaterPages=_draw_page_chrome)
    return output_path


if __name__ == "__main__":
    pdf_out = build_pdf()
    print(f"Reporte PDF generado exitosamente en: {pdf_out}")
