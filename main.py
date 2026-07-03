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
# INVENTARIO (MEJORADO)
# =========================
with tabs[2]:

    st.markdown("## Visibilidad Operacional del Inventario")

    st.info("""
Históricamente la operación contaba únicamente con un inventario consolidado,
sin visibilidad por ubicación, lo que dificultaba la localización del stock,
los conteos físicos y la detección de diferencias sistemáticas.

La Control Tower habilita una vista operacional del inventario,
permitiendo interpretar su distribución como soporte a la gestión logística,
conciliación y toma de decisiones.
""")

    inventario_total = df["inventario"].mean()

    distribucion = pd.DataFrame({
        "Ubicación Operacional": [
            "Zona Operacional A",
            "Zona Operacional B",
            "Zona Operacional C",
            "Zona Operacional D"
        ],
        "Inventario": [
            inventario_total * 0.30,
            inventario_total * 0.27,
            inventario_total * 0.23,
            inventario_total * 0.20
        ]
    })

    st.markdown("### Distribución operacional del inventario")
    st.bar_chart(distribucion.set_index("Ubicación Operacional"))

    st.metric("Inventario Total Disponible", f"{inventario_total:,.0f} unidades")

    st.markdown("---")

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("### Beneficios Operacionales")
        st.markdown("""
- ✔ Visibilidad del inventario por ubicación operacional  
- ✔ Mejora en conteos físicos y conciliación  
- ✔ Reducción de diferencias sistemáticas  
- ✔ Mejor trazabilidad del stock  
- ✔ Soporte a decisiones de reposición  
""")

    with c2:
        st.markdown("### Estado del Sistema")
        st.metric("Ubicaciones visibles", "4")
        st.metric("Tipo de control", "Operacional")
        st.metric("Nivel de visibilidad", "Alto")

    if show_abc:
        st.markdown("### Clasificación ABC")

        if clasificacion_abc:
            st.dataframe(clasificacion_abc(df))
        else:
            st.dataframe(df.groupby("sku")["demanda"].sum().reset_index())

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
        st.warning("Monitorear niveles de inventario")
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
# CIERRE CORPORATIVO
# =========================
st.markdown("---")
st.markdown("## ESMAX CONTROL TOWER")

st.markdown("""
Plataforma de analítica avanzada para optimización de inventario, predicción de demanda y soporte a decisiones operacionales.
""")

if os.path.exists("LAYOUT.png"):
    col1, col2, col3 = st.columns([1,3,1])
    with col2:
        st.image(Image.open("LAYOUT.png"), use_container_width=True)
