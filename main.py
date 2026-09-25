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
# ESTILO
# ============================================================

st.markdown("""
<style>

.kpi {
    background: linear-gradient(90deg,#123b5d,#176b9c);
    color:white;
    padding:16px;
    border-radius:12px;
    text-align:center;
    font-weight:bold;
    font-size:18px;
}

.card {
    background:white;
    padding:16px;
    border-radius:12px;
    box-shadow:0px 1px 6px rgba(0,0,0,0.08);
    border:1px solid #e5e7eb;
}

.title {
    font-size:32px;
    font-weight:800;
    color:#123b5d;
}

.subtitle {
    font-size:16px;
    color:#64748b;
}

.section {
    font-size:22px;
    font-weight:700;
    color:#123b5d;
    margin-top:20px;
}

.info {
    background:#eff6ff;
    padding:16px;
    border-radius:10px;
    border-left:5px solid #2563eb;
}

.success {
    background:#f0fdf4;
    padding:16px;
    border-radius:10px;
    border-left:5px solid #22c55e;
}

.warning {
    background:#fff7ed;
    padding:16px;
    border-radius:10px;
    border-left:5px solid #f97316;
}

</style>
""", unsafe_allow_html=True)

# ============================================================
# IMPORTACIÓN DE MÓDULOS
# ============================================================

try:
    from modules.data_generator import generar_dataset_ccu
except Exception:
    generar_dataset_ccu = None

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

dias = st.sidebar.slider(
    "Horizonte de análisis",
    30,
    365,
    180
)

st.sidebar.markdown("---")

st.sidebar.caption(
    "Plataforma demostrativa para evaluación "
    "de una cadena de suministro predictiva."
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

    if generar_dataset_ccu:

        df = generar_dataset_ccu(dias)

    else:

        # Datos de respaldo
        fechas = pd.date_range(
            start="2025-01-01",
            periods=dias,
            freq="D"
        )

        np.random.seed(42)

        demanda = (
            1000
            + 150 * np.sin(
                np.arange(dias) / 30
            )
            + np.random.normal(
                0,
                70,
                dias
            )
        )

        ventas = demanda * np.random.uniform(
            0.90,
            1.02,
            dias
        )

        inventario = np.maximum(
            3000 - np.cumsum(
                demanda - ventas
            ),
            500
        )

        df = pd.DataFrame({

            "fecha": fechas,

            "sku": np.random.choice(
                [
                    "Cerveza",
                    "Bebidas",
                    "Agua",
                    "Energéticas",
                    "Néctares"
                ],
                dias
            ),

            "demanda": demanda,

            "ventas": ventas,

            "inventario": inventario

        })


# ============================================================
# KPIs
# ============================================================

if calcular_kpis:

    kpis = calcular_kpis(df)

else:

    fill_rate = (
        df["ventas"] /
        df["demanda"]
    ).clip(0, 1).mean()

    mae = (
        df["demanda"] -
        df["ventas"]
    ).abs().mean()

    inventario_prom = (
        df["inventario"].mean()
    )

    kpis = {

        "fill_rate": fill_rate,

        "mae": mae,

        "inventario_prom": inventario_prom

    }


# ============================================================
# OPTIMIZACIÓN
# ============================================================

if optimizar_inventario:

    optim = optimizar_inventario(df)

else:

    optim = {

        "suggested_order": 0,

        "reorder_point": 0,

        "stock_seguridad": 0,

        "eoq": 0

    }


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="title">CCU Predictive Supply Chain</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Plataforma de planificación predictiva para la cadena de suministro'
    '</div>',
    unsafe_allow_html=True
)

st.markdown("---")


# ============================================================
# MENÚ
# ============================================================

tabs = st.tabs([

    "Dashboard Ejecutivo",

    "Demanda Predictiva",

    "Inventario",

    "Distribución",

    "Optimización",

    "Evaluación",

    "Diagnóstico"

])


# ============================================================
# DASHBOARD EJECUTIVO
# ============================================================

with tabs[0]:

    st.markdown(
        '<div class="section">Visión Ejecutiva</div>',
        unsafe_allow_html=True
    )

    st.markdown("""
    <div class="info">

    <b>Objetivo del proyecto</b>

    <br><br>

    Utilizar analítica predictiva para anticipar la demanda,
    mejorar la planificación de inventarios y optimizar la
    distribución de productos.

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
        <b>Desviación de demanda</b><br><br>
        {kpis['mae']:.1f}
        </div>
        """,
        unsafe_allow_html=True
    )

    c3.markdown(
        f"""
        <div class="card">
        <b>Inventario promedio</b><br><br>
        {kpis['inventario_prom']:,.0f}
        </div>
        """,
        unsafe_allow_html=True
    )

    c4.markdown(
        """
        <div class="card">
        <b>Estado de red</b><br><br>
        🟢 Operación controlada
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")

    st.markdown(
        '<div class="section">Cadena de suministro predictiva</div>',
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
            label="Demanda\\nhistórica",
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
            label="Optimización\\nde transporte",
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

        datos [
            label="Datos reales",
            fillcolor="#123b5d",
            fontcolor="white"
        ];

        demanda -> forecast;

        forecast -> inventario;

        inventario -> transporte;

        transporte -> rutas;

        rutas -> distribucion;

        distribucion -> datos;

        datos -> forecast;

    }

    """)

    st.markdown("---")

    st.markdown(
        '<div class="section">Resultado esperado</div>',
        unsafe_allow_html=True
    )

    a, b, c = st.columns(3)

    a.markdown("""
    <div class="success">
    <b>Menores costos</b><br><br>
    Optimización de cargas, rutas y utilización de vehículos.
    </div>
    """, unsafe_allow_html=True)

    b.markdown("""
    <div class="success">
    <b>Mayor nivel de servicio</b><br><br>
    Anticipación de demanda y reducción del riesgo de quiebres.
    </div>
    """, unsafe_allow_html=True)

    c.markdown("""
    <div class="success">
    <b>Mejor utilización de recursos</b><br><br>
    Inventario y capacidad logística alineados con la demanda.
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# DEMANDA
# ============================================================

with tabs[1]:

    st.markdown("## Demanda Predictiva")

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

    if "fecha" in df_fc.columns:

        st.line_chart(
            df_fc.set_index("fecha")
            [["demanda", "forecast"]]
        )

    else:

        st.line_chart(
            df_fc[["demanda", "forecast"]]
        )

    st.info("""
    El módulo predictivo permite anticipar variaciones de demanda
    y utilizar esa información para planificar inventarios,
    producción y distribución.
    """)


# ============================================================
# INVENTARIO
# ============================================================

with tabs[2]:

    st.markdown("## Gestión Predictiva de Inventario")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Inventario promedio",
        f"{kpis['inventario_prom']:,.0f}"
    )

    c2.metric(
        "Stock de seguridad",
        f"{optim.get('stock_seguridad', 0):,.0f}"
    )

    c3.metric(
        "Punto de reorden",
        f"{optim.get('reorder_point', 0):,.0f}"
    )

    st.markdown("---")

    if "fecha" in df.columns:

        st.line_chart(
            df.set_index("fecha")
            [["inventario"]]
        )

    if clasificacion_abc:

        st.markdown("### Clasificación ABC")

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


# ============================================================
# DISTRIBUCIÓN
# ============================================================

with tabs[3]:

    st.markdown("## 🚚 Distribución Predictiva")

    st.markdown("""
    <div class="info">

    <b>Objetivo:</b>

    Anticipar las necesidades de distribución y utilizar
    la información predictiva para mejorar la planificación
    de cargas, vehículos y recorridos.

    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Indicadores de distribución")

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
        "Km optimizados",
        "-11.8%"
    )

    c4.metric(
        "Riesgo de quiebre",
        "2.8%"
    )

    st.markdown("---")

    st.markdown("### Simulación de demanda")

    aumento = st.slider(
        "Variación proyectada de demanda",
        -20,
        30,
        10
    )

    capacidad = st.slider(
        "Capacidad disponible de transporte",
        50,
        100,
        85
    )

    demanda_base = df["demanda"].sum()

    demanda_proyectada = (
        demanda_base *
        (1 + aumento / 100)
    )

    utilizacion = (
        demanda_proyectada /
        demanda_base
    ) * (
        91.4 /
        capacidad * 100
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

    st.markdown("### Flujo de decisión")

    st.markdown("""
    **Pronóstico de demanda**

    ↓

    **Planificación de inventario**

    ↓

    **Planificación de carga**

    ↓

    **Asignación de vehículos**

    ↓

    **Optimización de rutas**

    ↓

    **Distribución al cliente**
    """)


# ============================================================
# OPTIMIZACIÓN
# ============================================================

with tabs[4]:

    st.markdown("## Optimización de Inventario")

    st.markdown(f"""
    **Pedido sugerido:** {optim.get('suggested_order', 0):,.0f}

    **Punto de reorden:** {optim.get('reorder_point', 0):,.1f}

    **Stock de seguridad:** {optim.get('stock_seguridad', 0):,.1f}

    **EOQ:** {optim.get('eoq', 0):,.1f}
    """)

    pedido = optim.get(
        "suggested_order",
        0
    )

    if pedido > 500:

        st.error(
            "ALTO: se recomienda revisar abastecimiento."
        )

    elif pedido > 0:

        st.warning(
            "MEDIO: se recomienda monitorear."
        )

    else:

        st.success(
            "BAJO: sistema estable."
        )


# ============================================================
# EVALUACIÓN
# ============================================================

with tabs[5]:

    st.markdown(
        "## Evaluación Preliminar del Proyecto"
    )

    st.info("""
    Los siguientes valores corresponden a un escenario
    demostrativo para evaluar económicamente la solución.
    No representan cifras oficiales de CCU.
    """)

    inversion = st.number_input(
        "Inversión inicial (MM$)",
        100,
        5000,
        800
    )

    ahorro = st.number_input(
        "Ahorro anual estimado (MM$)",
        20,
        2000,
        250
    )

    beneficio = st.number_input(
        "Beneficio operacional anual (MM$)",
        0,
        2000,
        80
    )

    flujo = ahorro + beneficio

    payback = (
        inversion / flujo
        if flujo > 0
        else 0
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Inversión",
        f"${inversion:,.0f} MM"
    )

    c2.metric(
        "Beneficio anual",
        f"${flujo:,.0f} MM"
    )

    c3.metric(
        "Payback",
        f"{payback:.2f} años"
    )


# ============================================================
# DIAGNÓSTICO
# ============================================================

with tabs[6]:

    st.markdown(
        "## Diagnóstico Estratégico"
    )

    foda1, foda2 = st.columns(2)

    with foda1:

        st.success("""
        ### Fortalezas

        - Amplia variedad de productos.
        - Trayectoria empresarial.
        - Red logística desarrollada.
        - Capacidad productiva.
        """)

        st.error("""
        ### Debilidades

        - Alta complejidad operacional.
        - Gran cantidad de SKUs.
        - Costos de distribución.
        """)

    with foda2:

        st.info("""
        ### Oportunidades

        - Inteligencia artificial.
        - Analítica predictiva.
        - Optimización de rutas.
        - Automatización.
        """)

        st.warning("""
        ### Amenazas

        - Combustible.
        - Materias primas.
        - Regulaciones.
        - Costos logísticos.
        """)

    st.markdown("---")

    st.markdown("""
    ### Oportunidad identificada

    La escala y complejidad de la cadena de suministro de CCU
    generan una oportunidad para implementar herramientas de
    analítica predictiva orientadas a demanda, inventario y
    distribución.

    El proyecto busca transformar una planificación
    principalmente reactiva hacia una gestión predictiva.
    """)


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "CCU Predictive Supply Chain | Proyecto académico | 2026"
)

st.caption(
    "Los datos operacionales y económicos utilizados en esta "
    "demostración son simulados."
)
