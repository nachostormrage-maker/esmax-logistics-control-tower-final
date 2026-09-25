import streamlit as st
from PIL import Image
import pandas as pd
import numpy as np
import os

# ============================================================
# CONFIGURACIÓN
# ============================================================

st.set_page_config(
    page_title="CCU Predictive Supply Chain",
    page_icon="🍺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# ESTILO VISUAL
# ============================================================

st.markdown("""
<style>

.kpi {
    background: linear-gradient(90deg,#123b5d,#176b9c);
    color: white;
    padding: 16px;
    border-radius: 12px;
    text-align: center;
    font-weight: bold;
    font-size: 18px;
}

.card {
    background: white;
    padding: 16px;
    border-radius: 12px;
    box-shadow: 0px 1px 6px rgba(0,0,0,0.08);
    border: 1px solid #e5e7eb;
}

.title {
    font-size: 32px;
    font-weight: 800;
    color: #123b5d;
    text-align: center;
}

.subtitle {
    font-size: 16px;
    color: #64748b;
    text-align: center;
}

.section {
    font-size: 22px;
    font-weight: 700;
    color: #123b5d;
    margin-top: 20px;
}

.info {
    background: #eff6ff;
    padding: 16px;
    border-radius: 10px;
    border-left: 5px solid #2563eb;
}

.success {
    background: #f0fdf4;
    padding: 16px;
    border-radius: 10px;
    border-left: 5px solid #22c55e;
}

.warning {
    background: #fff7ed;
    padding: 16px;
    border-radius: 10px;
    border-left: 5px solid #f97316;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# IMPORTACIÓN DE MÓDULOS
# ============================================================

try:
    from modules.data_generator import generar_dataset_esmax
except Exception:
    generar_dataset_esmax = None

try:
    from modules.inventory import calcular_kpis, clasificacion_abc
except Exception:
    calcular_kpis = None
    clasificacion_abc = None

try:
    from modules.forecast import generar_forecast
except Exception:
    generar_forecast = None

try:
    from modules.inventory_optimizer import optimizar_inventario
except Exception:
    optimizar_inventario = None

try:
    from modules.pdf_report import generar_pdf_bytes
except Exception:
    generar_pdf_bytes = None


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("🍺 CCU")

st.sidebar.markdown(
    "**Predictive Supply Chain**"
)

st.sidebar.markdown("---")

uploaded = st.sidebar.file_uploader(
    "Subir datos",
    type=["csv", "xlsx"]
)

use_sample = st.sidebar.checkbox(
    "Usar datos simulados",
    True
)

dias = st.sidebar.slider(
    "Horizonte de análisis (días)",
    30,
    365,
    180
)

st.sidebar.markdown("---")

st.sidebar.markdown(
    "### Módulos"
)

show_kpis = st.sidebar.checkbox(
    "KPIs",
    True
)

show_graphs = st.sidebar.checkbox(
    "Gráficos",
    True
)

show_abc = st.sidebar.checkbox(
    "Clasificación ABC",
    True
)

show_opt = st.sidebar.checkbox(
    "Optimización",
    True
)

# ============================================================
# DATA
# ============================================================

if uploaded:

    if uploaded.name.endswith(".csv"):
        df = pd.read_csv(uploaded)
    else:
        df = pd.read_excel(uploaded)

else:

    if use_sample and generar_dataset_esmax:
        df = generar_dataset_esmax(dias)
    else:
        df = None


if df is None:

    st.error(
        "No hay datos disponibles. "
        "Sube un archivo o activa los datos simulados."
    )

    st.stop()


# ============================================================
# KPIs
# ============================================================

if calcular_kpis:

    kpis = calcular_kpis(df)

else:

    kpis = {

        "fill_rate": (
            df["ventas"] / df["demanda"]
        ).mean(),

        "mae": (
            df["demanda"] -
            df.get("ventas", 0)
        ).abs().mean(),

        "inventario_prom": (
            df["inventario"].mean()
        )
    }


# ============================================================
# OPTIMIZACIÓN
# ============================================================

if optimizar_inventario:

    optim = optimizar_inventario(df)

else:

    optim = {}


# ============================================================
# NIVEL DE RIESGO
# ============================================================

riesgo = "BAJO"

if optim.get("suggested_order", 0) > 500:

    riesgo = "ALTO"

elif optim.get("suggested_order", 0) > 0:

    riesgo = "MEDIO"


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="title">'
    'CCU PREDICTIVE SUPPLY CHAIN'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Plataforma de analítica predictiva para la cadena de suministro'
    '</div>',
    unsafe_allow_html=True
)

st.markdown("---")


# ============================================================
# TABS
# ============================================================

tabs = st.tabs([

    "Dashboard Ejecutivo",

    "Forecast",

    "Inventario",

    "Distribución",

    "Optimización",

    "Diagnóstico",

    "Reporte"

])


# ============================================================
# DASHBOARD EJECUTIVO
# ============================================================

with tabs[0]:

    st.markdown(
        '<div class="section">'
        'Visión Ejecutiva'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown("""
    <div class="info">

    <b>Objetivo de la plataforma</b>

    <br><br>

    Apoyar la toma de decisiones de la cadena de suministro
    mediante pronóstico de demanda, gestión de inventarios
    y planificación de la distribución.

    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Indicadores clave")

    c1, c2, c3, c4 = st.columns(4)

    c1.markdown(
        f"""
        <div class="kpi">
        Fill Rate<br>
        {kpis['fill_rate']:.1%}
        </div>
        """,
        unsafe_allow_html=True
    )

    c2.markdown(
        f"""
        <div class="card">
        <b>Desviación de demanda</b>
        <br><br>
        {kpis['mae']:.1f}
        </div>
        """,
        unsafe_allow_html=True
    )

    c3.markdown(
        f"""
        <div class="card">
        <b>Inventario promedio</b>
        <br><br>
        {kpis['inventario_prom']:,.0f}
        </div>
        """,
        unsafe_allow_html=True
    )

    c4.markdown(
        f"""
        <div class="card">
        <b>Nivel de riesgo</b>
        <br><br>
        {riesgo}
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")

    st.markdown(
        '<div class="section">'
        'Cadena de suministro predictiva'
        '</div>',
        unsafe_allow_html=True
    )

    st.graphviz_chart("""

    digraph {

        rankdir=LR;

        node [
            shape=box,
            style="rounded,filled",
            fontname="Arial"
        ];

        demanda [
            label="Datos de\\ndemanda",
            fillcolor="#dbeafe"
        ];

        forecast [
            label="Pronóstico\\npredictivo",
            fillcolor="#bfdbfe"
        ];

        inventario [
            label="Planificación\\nde inventario",
            fillcolor="#93c5fd"
        ];

        transporte [
            label="Planificación\\nde transporte",
            fillcolor="#60a5fa"
        ];

        rutas [
            label="Optimización\\nde rutas",
            fillcolor="#3b82f6",
            fontcolor="white"
        ];

        distribucion [
            label="Distribución",
            fillcolor="#2563eb",
            fontcolor="white"
        ];

        cliente [
            label="Cliente",
            fillcolor="#123b5d",
            fontcolor="white"
        ];

        demanda -> forecast;

        forecast -> inventario;

        inventario -> transporte;

        transporte -> rutas;

        rutas -> distribucion;

        distribucion -> cliente;

        cliente -> demanda;

    }

    """)

    st.markdown("---")

    st.markdown("### Impacto esperado")

    c1, c2, c3 = st.columns(3)

    c1.markdown("""
    <div class="success">

    <b>Menores costos logísticos</b>

    <br><br>

    Mejor planificación de cargas,
    recorridos y utilización de vehículos.

    </div>
    """, unsafe_allow_html=True)

    c2.markdown("""
    <div class="success">

    <b>Mayor nivel de servicio</b>

    <br><br>

    Anticipación de demanda y
    reducción del riesgo de quiebres.

    </div>
    """, unsafe_allow_html=True)

    c3.markdown("""
    <div class="success">

    <b>Mejor planificación</b>

    <br><br>

    Integración entre demanda,
    inventario y distribución.

    </div>
    """, unsafe_allow_html=True)


# ============================================================
# FORECAST
# ============================================================

with tabs[1]:

    st.markdown("## Pronóstico de Demanda")

    st.markdown("""
    <div class="info">

    El pronóstico permite anticipar el comportamiento de la
    demanda y utilizar esta información para apoyar las decisiones
    de inventario, abastecimiento y distribución.

    </div>
    """, unsafe_allow_html=True)

    if generar_forecast:

        df_fc = generar_forecast(df)

        if isinstance(df_fc, tuple):
            df_fc = df_fc[0]

    else:

        df_fc = df.copy()

        df_fc["forecast"] = (
            df_fc["demanda"]
            .rolling(7)
            .mean()
        )

    if "forecast" not in df_fc.columns:

        df_fc["forecast"] = (
            df_fc["demanda"]
            .rolling(7)
            .mean()
        )

    if "fecha" in df_fc.columns:

        st.line_chart(
            df_fc.set_index("fecha")
            [["demanda", "forecast"]]
        )

    else:

        st.line_chart(
            df_fc[["demanda", "forecast"]]
        )

    st.markdown("### Datos del pronóstico")

    st.dataframe(
        df_fc.tail(20),
        use_container_width=True
    )


# ============================================================
# INVENTARIO
# ============================================================

with tabs[2]:

    st.markdown(
        "## Gestión Predictiva de Inventario"
    )

    st.markdown("""
    <div class="info">

    La gestión predictiva permite utilizar el comportamiento
    esperado de la demanda para definir niveles de inventario,
    stock de seguridad y puntos de reorden.

    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Inventario promedio",
        f"{kpis['inventario_prom']:,.0f}"
    )

    col2.metric(
        "Stock de seguridad",
        f"{optim.get('stock_seguridad', 0):,.0f}"
    )

    col3.metric(
        "Punto de reorden",
        f"{optim.get('reorder_point', 0):,.0f}"
    )

    st.markdown("---")

    if "fecha" in df.columns:

        st.markdown(
            "### Evolución del inventario"
        )

        st.line_chart(
            df.set_index("fecha")
            [["inventario"]]
        )

    if show_abc:

        st.markdown(
            "### Clasificación ABC"
        )

        if clasificacion_abc:

            try:

                abc = clasificacion_abc(df)

                st.dataframe(
                    abc,
                    use_container_width=True
                )

            except Exception:

                st.warning(
                    "No fue posible generar la clasificación ABC."
                )

        else:

            if "sku" in df.columns:

                st.dataframe(
                    df.groupby("sku")
                    ["demanda"]
                    .sum()
                    .reset_index(),
                    use_container_width=True
                )


# ============================================================
# DISTRIBUCIÓN
# ============================================================

with tabs[3]:

    st.markdown(
        "## 🚚 Distribución Predictiva"
    )

    st.markdown("""
    <div class="info">

    <b>Oportunidad identificada:</b>

    Mejorar la planificación de la distribución mediante
    información predictiva de demanda, inventario y capacidad
    de transporte.

    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        "### Indicadores de distribución"
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Utilización de flota",
        "91.4%"
    )

    c2.metric(
        "Entregas a tiempo",
        "95.2%"
    )

    c3.metric(
        "Distancia optimizable",
        "11.8%"
    )

    c4.metric(
        "Riesgo de quiebre",
        "2.8%"
    )

    st.markdown("---")

    st.markdown(
        "### Simulador de capacidad logística"
    )

    aumento = st.slider(
        "Variación proyectada de demanda (%)",
        -20,
        30,
        10
    )

    capacidad = st.slider(
        "Capacidad disponible de transporte (%)",
        50,
        120,
        85
    )

    demanda_base = df["demanda"].sum()

    demanda_proyectada = (
        demanda_base *
        (1 + aumento / 100)
    )

    utilizacion = (
        91.4 *
        (demanda_proyectada / demanda_base) *
        (85 / capacidad)
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Demanda proyectada",
        f"{demanda_proyectada:,.0f}"
    )

    c2.metric(
        "Utilización estimada",
        f"{utilizacion:.1f}%"
    )

    if utilizacion > 100:

        c3.error(
            "⚠️ Capacidad insuficiente"
        )

    elif utilizacion > 90:

        c3.warning(
            "⚠️ Capacidad tensionada"
        )

    else:

        c3.success(
            "✓ Capacidad adecuada"
        )

    st.markdown("---")

    st.markdown(
        "### Flujo de decisión"
    )

    st.markdown("""
    **1. Pronóstico de demanda**

    ↓

    **2. Planificación de inventario**

    ↓

    **3. Planificación de carga**

    ↓

    **4. Asignación de vehículos**

    ↓

    **5. Optimización de rutas**

    ↓

    **6. Distribución al cliente**
    """)


# ============================================================
# OPTIMIZACIÓN
# ============================================================

with tabs[4]:

    st.markdown(
        "## Optimización de Inventario"
    )

    st.markdown("""
    <div class="info">

    El módulo de optimización transforma la información
    predictiva en una recomendación de reposición.

    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Pedido sugerido",
        f"{optim.get('suggested_order', 0):,.0f}"
    )

    c2.metric(
        "Punto de reorden",
        f"{optim.get('reorder_point', 0):,.1f}"
    )

    c3.metric(
        "Stock seguridad",
        f"{optim.get('stock_seguridad', 0):,.1f}"
    )

    c4.metric(
        "EOQ",
        f"{optim.get('eoq', 0):,.1f}"
    )

    st.markdown("---")

    if riesgo == "ALTO":

        st.error(
            "ALTO: revisar abastecimiento y capacidad logística."
        )

    elif riesgo == "MEDIO":

        st.warning(
            "MEDIO: se recomienda monitoreo."
        )

    else:

        st.success(
            "BAJO: operación estable."
        )


# ============================================================
# DIAGNÓSTICO
# ============================================================

with tabs[5]:

    st.markdown(
        "## Diagnóstico Estratégico"
    )

    st.markdown("""
    <div class="info">

    Esta sección conecta la plataforma con el diagnóstico
    realizado en el informe de evaluación del proyecto.

    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:

        st.success("""
        ### Fortalezas

        - Amplia variedad de productos y marcas.
        - Trayectoria empresarial.
        - Red de producción y distribución.
        - Capacidad industrial.
        - Presencia en diferentes categorías de bebestibles.
        """)

        st.error("""
        ### Debilidades

        - Alta complejidad operacional.
        - Gran cantidad de productos y SKUs.
        - Complejidad de distribución a gran escala.
        - Costos logísticos.
        """)

    with col2:

        st.info("""
        ### Oportunidades

        - Inteligencia artificial.
        - Analítica predictiva.
        - Optimización de rutas.
        - Automatización.
        - Crecimiento de canales digitales.
        """)

        st.warning("""
        ### Amenazas

        - Aumento de costos de transporte.
        - Variación de combustibles.
        - Variación de materias primas.
        - Cambios regulatorios.
        """)

    st.markdown("---")

    st.markdown(
        "### Oportunidad de mejora identificada"
    )

    st.markdown("""
    La escala y complejidad de la cadena de suministro de CCU
    generan una oportunidad para incorporar herramientas de
    analítica predictiva.

    La solución busca conectar el pronóstico de demanda con
    la planificación de inventarios y distribución.

    De esta forma, la gestión puede evolucionar desde una
    planificación principalmente reactiva hacia una planificación
    basada en información predictiva.
    """)


# ============================================================
# REPORTE
# ============================================================

with tabs[6]:

    st.markdown(
        "## Reporte Ejecutivo"
    )

    st.markdown("""
    <div class="info">

    El reporte ejecutivo resume los principales indicadores
    obtenidos desde la plataforma y puede utilizarse como apoyo
    para la evaluación del proyecto.

    </div>
    """, unsafe_allow_html=True)

    if generar_pdf_bytes:

        try:

            pdf = generar_pdf_bytes(
                df,
                kpis
            )

            st.download_button(
                "📄 Descargar reporte PDF",
                pdf,
                "CCU_Predictive_Supply_Chain_Report.pdf",
                mime="application/pdf"
            )

        except Exception:

            st.warning(
                "El módulo de reporte todavía requiere adaptación a CCU."
            )

    else:

        st.info(
            "El módulo PDF no está disponible."
        )


# ============================================================
# CIERRE
# ============================================================

st.markdown("---")

st.markdown(
    "## CCU PREDICTIVE SUPPLY CHAIN"
)

st.markdown("""
Plataforma demostrativa de analítica avanzada para apoyar
decisiones de demanda, inventario y distribución dentro
de una cadena de suministro de bebestibles.
""")

st.caption(
    "Proyecto académico | Evaluación de Proyectos para Cadena de Suministros | 2026"
)

st.caption(
    "Los datos operacionales utilizados en esta demostración "
    "son simulados y no representan información confidencial de CCU."
)

# ============================================================
# LAYOUT
# ============================================================

if os.path.exists("LAYOUT.png"):

    st.markdown("---")

    st.markdown(
        "### Arquitectura de la solución"
    )

    col1, col2, col3 = st.columns([1, 3, 1])

    with col2:

        st.image(
            Image.open("LAYOUT.png"),
            use_container_width=True
        )
