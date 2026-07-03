import streamlit as st
from PIL import Image
import pandas as pd
import numpy as np
import os

# =========================
# CONFIGURACIÓN
# =========================
st.set_page_config(
    page_title="ESMAX Control Tower",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# ESTILO VISUAL
# =========================
st.markdown("""
<style>
.kpi {
    background: linear-gradient(90deg,#0b5f8a,#0b9bd3);
    color:white;
    padding:14px;
    border-radius:12px;
    text-align:center;
    font-weight:bold;
}

.card {
    background:white;
    padding:12px;
    border-radius:12px;
    box-shadow:0px 1px 6px rgba(0,0,0,0.08);
}

.title {
    font-size:28px;
    font-weight:800;
    color:#0b5f8a;
    text-align:center;
}
</style>
""", unsafe_allow_html=True)

# =========================
# IMPORTACIÓN DE MÓDULOS
# =========================
try:
    from modules.data_generator import generar_dataset_esmax
except:
    generar_dataset_esmax = None

try:
    from modules.inventory import calcular_kpis, clasificacion_abc
except:
    calcular_kpis = None
    clasificacion_abc = None

try:
    from modules.forecast import generar_forecast
except:
    generar_forecast = None

try:
    from modules.inventory_optimizer import optimizar_inventario
except:
    optimizar_inventario = None

try:
    from modules.pdf_report import generar_pdf_bytes
except:
    generar_pdf_bytes = None

# =========================
# SIDEBAR
# =========================
st.sidebar.header("Panel de Control")

uploaded = st.sidebar.file_uploader("Subir datos (CSV/XLSX)", type=["csv","xlsx"])
use_sample = st.sidebar.checkbox("Usar datos simulados", True)
dias = st.sidebar.slider("Horizonte de análisis (días)", 30, 365, 180)

show_kpis = st.sidebar.checkbox("KPIs", True)
show_graphs = st.sidebar.checkbox("Gráficos", True)
show_abc = st.sidebar.checkbox("ABC", True)
show_opt = st.sidebar.checkbox("Optimización", True)

# =========================
# DATA
# =========================
if uploaded:
    df = pd.read_csv(uploaded) if uploaded.name.endswith(".csv") else pd.read_excel(uploaded)
else:
    df = generar_dataset_esmax(dias) if generar_dataset_esmax else None

if df is None:
    st.error("No hay datos disponibles")
    st.stop()

# =========================
# KPIs
# =========================
if calcular_kpis:
    kpis = calcular_kpis(df)
else:
    kpis = {
        "fill_rate": (df["ventas"]/df["demanda"]).mean(),
        "mae": (df["demanda"] - df.get("ventas",0)).abs().mean(),
        "inventario_prom": df["inventario"].mean()
    }

# =========================
# OPTIMIZACIÓN
# =========================
optim = optimizar_inventario(df) if optimizar_inventario else {}

riesgo = "BAJO"
if optim.get("suggested_order",0) > 500:
    riesgo = "ALTO"
elif optim.get("suggested_order",0) > 0:
    riesgo = "MEDIO"

# =========================
# HEADER
# =========================
st.markdown('<div class="title">ESMAX CONTROL TOWER</div>', unsafe_allow_html=True)
st.markdown("---")

# =========================
# TABS
# =========================
tabs = st.tabs([
    "Dashboard",
    "Forecast",
    "Inventario",
    "Optimización",
    "Reporte"
])

# =========================
# DASHBOARD
# =========================
with tabs[0]:
    st.markdown("### Indicadores clave")

    c1,c2,c3 = st.columns(3)

    c1.markdown(f"<div class='kpi'>Fill Rate<br>{kpis['fill_rate']:.2%}</div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='card'><b>Desviación de Demanda</b><br>{kpis['mae']:.1f}</div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='card'><b>Inventario Prom</b><br>{kpis['inventario_prom']:.0f}</div>", unsafe_allow_html=True)

    st.markdown("### Datos")
    st.dataframe(df.head(20), use_container_width=True)

    if show_graphs:
        st.markdown("### Tendencias")
        if "fecha" in df.columns:
            st.line_chart(df.set_index("fecha")[["demanda","ventas","inventario"]])
        else:
            st.line_chart(df[["demanda","ventas","inventario"]])

# =========================
# FORECAST
# =========================
with tabs[1]:
    st.markdown("### Pronóstico")

    df_fc = generar_forecast(df) if generar_forecast else df.copy()

    if isinstance(df_fc, tuple):
        df_fc = df_fc[0]

    df_fc["forecast"] = df_fc.get("forecast", df_fc["demanda"].rolling(7).mean())

    st.line_chart(df_fc.set_index("fecha")[["demanda","forecast"]])

# =========================
# INVENTARIO (VERSIÓN EJECUTIVA)
# =========================
with tabs[2]:

    st.markdown("## Visión Operacional del Inventario")

    st.markdown("""
    <div style='background:#f5f7fa;padding:14px;border-radius:12px;
    border-left:5px solid #0b5f8a;'>
    Históricamente el inventario se gestionaba como una cifra consolidada,
    sin visibilidad operacional. Esto generaba dificultades en trazabilidad,
    conteos físicos y diferencias sistemáticas.
    <br><br>
    La Control Tower transforma esta visión hacia un modelo distribuido,
    permitiendo interpretar el inventario como una red operacional de disponibilidad.
    </div>
    """, unsafe_allow_html=True)

    inventario_total = df["inventario"].mean()

    col1, col2, col3 = st.columns(3)

    col1.metric("Inventario Total", f"{inventario_total:,.0f}")
    col2.metric("Ubicaciones", "4")
    col3.metric("Visibilidad", "Alta")

    st.markdown("---")

    distribucion = pd.DataFrame({
        "Ubicación Operacional": [
            "Zona Operacional A",
            "Zona Operacional B",
            "Zona Operacional C",
            "Zona Operacional D"
        ],
        "Inventario": [
            inventario_total * 0.33,
            inventario_total * 0.27,
            inventario_total * 0.22,
            inventario_total * 0.18
        ]
    })

    c1, c2 = st.columns([2,1])

    with c1:
        st.markdown("### Distribución Operacional")
        st.bar_chart(distribucion.set_index("Ubicación Operacional"))

    with c2:
        st.markdown("### Participación")
        distribucion["%"] = distribucion["Inventario"] / distribucion["Inventario"].sum()
        st.dataframe(distribucion[["Ubicación Operacional","%"]].style.format({"%":"{:.1%}"}))

    st.markdown("---")

    c1, c2, c3 = st.columns(3)

    c1.markdown("<div class='card'><b>Estado</b><br>Controlado</div>", unsafe_allow_html=True)
    c2.markdown("<div class='card'><b>Riesgo</b><br>Bajo</div>", unsafe_allow_html=True)
    c3.markdown("<div class='card'><b>Gestión</b><br>Operacional</div>", unsafe_allow_html=True)

    st.markdown("### Impacto Operacional")

    st.markdown("""
    - ✔ Visibilidad por ubicación operacional  
    - ✔ Reducción de diferencias de inventario  
    - ✔ Mejora en conciliación física  
    - ✔ Apoyo a reposición y planificación  
    - ✔ Trazabilidad del stock  
    """)

    if show_abc:
        st.markdown("### Clasificación ABC")

        if clasificacion_abc:
            st.dataframe(clasificacion_abc(df), use_container_width=True)
        else:
            st.dataframe(df.groupby("sku")["demanda"].sum().reset_index(), use_container_width=True)

# =========================
# OPTIMIZACIÓN
# =========================
with tabs[3]:
    st.markdown("### Decisión de reposición")

    st.markdown(f"""
- Riesgo operativo: **{riesgo}**
- Pedido sugerido: **{optim.get('suggested_order',0):.0f}**
- Punto de reorden: **{optim.get('reorder_point',0):.1f}**
- Stock de seguridad: **{optim.get('stock_seguridad',0):.1f}**
- EOQ: **{optim.get('eoq',0):.1f}**
""")

    if riesgo == "ALTO":
        st.error("Acción inmediata requerida")
    elif riesgo == "MEDIO":
        st.warning("Monitoreo requerido")
    else:
        st.success("Sistema estable")

# =========================
# REPORTE
# =========================
with tabs[4]:
    st.markdown("### Reporte ejecutivo")

    if generar_pdf_bytes:
        pdf = generar_pdf_bytes(df, kpis)
        st.download_button("Descargar PDF", pdf, "ESMAX_Report.pdf")

# =========================
# CIERRE
# =========================
st.markdown("---")
st.markdown("## ESMAX CONTROL TOWER")

st.markdown("""
Plataforma de analítica avanzada para soporte a decisiones logísticas, optimización de inventario y control operacional.
""")

if os.path.exists("LAYOUT.png"):
    col1, col2, col3 = st.columns([1,3,1])
    with col2:
        st.image(Image.open("LAYOUT.png"), use_container_width=True)
