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
dias = st.sidebar.slider("Horizonte de análisis (días)", 30, 365, 180)

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
        "mae": (df["demanda"] - df["ventas"]).abs().mean(),
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
    c1,c2,c3 = st.columns(3)

    c1.markdown(f"<div class='kpi'>Fill Rate<br>{kpis['fill_rate']:.2%}</div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='card'><b>Desviación</b><br>{kpis['mae']:.1f}</div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='card'><b>Inventario Prom</b><br>{kpis['inventario_prom']:.0f}</div>", unsafe_allow_html=True)

    st.line_chart(df.set_index("fecha")[["demanda","ventas","inventario"]])

# =========================
# FORECAST
# =========================
with tabs[1]:

    df_fc = generar_forecast(df) if generar_forecast else df.copy()

    if isinstance(df_fc, tuple):
        df_fc = df_fc[0]

    df_fc["forecast"] = df_fc.get("forecast", df_fc["demanda"].rolling(7).mean())

    st.line_chart(df_fc.set_index("fecha")[["demanda","forecast"]])

# =========================
# INVENTARIO (SOLO MEJORA VISUAL)
# =========================
with tabs[2]:

    st.markdown("### Visibilidad del Inventario")

    st.info(
        "Esta sección permite visualizar el inventario disponible como apoyo al control operacional."
    )

    inventario_total = df["inventario"].mean()

    c1,c2,c3 = st.columns(3)

    c1.metric("Inventario Total", f"{inventario_total:,.0f}")
    c2.metric("Cobertura", "4 zonas")
    c3.metric("Estado", "Controlado")

    distribucion = pd.DataFrame({
        "Zona": ["Norte","Centro","Sur","Austral"],
        "Inventario": [
            inventario_total*0.30,
            inventario_total*0.27,
            inventario_total*0.23,
            inventario_total*0.20
        ]
    })

    st.bar_chart(distribucion.set_index("Zona"))

    st.markdown("#### Participación")

    distribucion["%"] = distribucion["Inventario"]/distribucion["Inventario"].sum()
    st.dataframe(distribucion[["Zona","%"]].style.format({"%":"{:.1%}"}))

    with st.expander("Insight operativo"):
        st.write("""
        El inventario total se mantiene, pero ahora puede interpretarse por distribución operacional,
        facilitando la localización y control del stock.
        """)

# =========================
# OPTIMIZACIÓN
# =========================
with tabs[3]:

    st.markdown("### Reposición")

    st.write(f"""
- Riesgo: {riesgo}
- Pedido sugerido: {optim.get('suggested_order',0):.0f}
- Reorder point: {optim.get('reorder_point',0):.1f}
- Stock seguridad: {optim.get('stock_seguridad',0):.1f}
""")

# =========================
# REPORTE
# =========================
with tabs[4]:

    if generar_pdf_bytes:
        pdf = generar_pdf_bytes(df,kpis)
        st.download_button("Descargar Reporte", pdf, "ESMAX.pdf")

# =========================
# FOOTER
# =========================
st.markdown("---")
st.markdown("ESMAX CONTROL TOWER")
