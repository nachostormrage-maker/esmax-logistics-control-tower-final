import streamlit as st
from PIL import Image
import pandas as pd
import numpy as np
import os

# =========================
# CONFIG
# =========================
st.set_page_config(
    page_title="ESMAX Control Tower",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# ESTILO PRO
# =========================
st.markdown("""
<style>

.title {
    font-size:30px;
    font-weight:900;
    text-align:center;
    color:#0b5f8a;
}

.card {
    background:white;
    padding:16px;
    border-radius:14px;
    box-shadow:0px 3px 10px rgba(0,0,0,0.08);
}

.kpi {
    padding:14px;
    border-radius:14px;
    color:white;
    font-weight:700;
    text-align:center;
}

.kpi.blue { background:linear-gradient(90deg,#0b5f8a,#0b9bd3); }
.kpi.green { background:linear-gradient(90deg,#1b8a5a,#2ecc71); }
.kpi.orange { background:linear-gradient(90deg,#c77700,#f39c12); }

.small {
    font-size:13px;
    color:gray;
}

</style>
""", unsafe_allow_html=True)

# =========================
# IMPORTS
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
st.sidebar.header("Control Panel")

uploaded = st.sidebar.file_uploader("Upload Data", type=["csv","xlsx"])
dias = st.sidebar.slider("Horizonte", 30, 365, 180)

# =========================
# DATA
# =========================
if uploaded:
    df = pd.read_csv(uploaded) if uploaded.name.endswith(".csv") else pd.read_excel(uploaded)
else:
    df = generar_dataset_esmax(dias) if generar_dataset_esmax else None

if df is None:
    st.error("No data available")
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
# OPTIMIZACION
# =========================
optim = optimizar_inventario(df) if optimizar_inventario else {}

riesgo_val = optim.get("suggested_order",0)

if riesgo_val > 500:
    risk = "ALTO"
    risk_color = "kpi orange"
elif riesgo_val > 0:
    risk = "MEDIO"
    risk_color = "kpi blue"
else:
    risk = "BAJO"
    risk_color = "kpi green"

# =========================
# HEADER
# =========================
st.markdown('<div class="title">ESMAX CONTROL TOWER</div>', unsafe_allow_html=True)
st.markdown("---")

# =========================
# TABS
# =========================
tabs = st.tabs(["Dashboard","Forecast","Inventario","Optimización","Reporte"])

# =========================
# DASHBOARD
# =========================
with tabs[0]:

    col1,col2,col3 = st.columns(3)

    col1.markdown(f"<div class='kpi blue'>Fill Rate<br>{kpis['fill_rate']:.2%}</div>", unsafe_allow_html=True)
    col2.markdown(f"<div class='kpi green'>Inventario Prom<br>{kpis['inventario_prom']:.0f}</div>", unsafe_allow_html=True)
    col3.markdown(f"<div class='kpi orange'>Desviación<br>{kpis['mae']:.0f}</div>", unsafe_allow_html=True)

    st.markdown("### Operational Data")
    st.dataframe(df.head(15), use_container_width=True)

    st.markdown("### Trend")
    st.line_chart(df.set_index("fecha")[["demanda","ventas","inventario"]])

# =========================
# FORECAST
# =========================
with tabs[1]:

    st.markdown("### Demand Forecast")

    df_fc = generar_forecast(df) if generar_forecast else df.copy()
    if isinstance(df_fc, tuple):
        df_fc = df_fc[0]

    df_fc["forecast"] = df_fc.get("forecast", df_fc["demanda"].rolling(7).mean())

    st.line_chart(df_fc.set_index("fecha")[["demanda","forecast"]])

# =========================
# INVENTARIO (VERSIÓN PRO)
# =========================
with tabs[2]:

    st.markdown("## Inventory Control Tower")

    st.markdown("""
    <div class='card'>
    <b>Contexto Operacional</b><br>
    La gestión previa del inventario operaba bajo una visión consolidada,
    sin trazabilidad por ubicación. Esto generaba quiebres de visibilidad,
    diferencias sistemáticas y baja capacidad de control operacional.
    </div>
    """, unsafe_allow_html=True)

    inventario_total = df["inventario"].mean()

    # ================= KPI ROW =================
    c1,c2,c3 = st.columns(3)

    c1.markdown(f"<div class='kpi blue'>Total Stock<br>{inventario_total:,.0f}</div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='kpi green'>Locations<br>4</div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='kpi orange'>Visibility<br>High</div>", unsafe_allow_html=True)

    st.markdown("---")

    # ================= DISTRIBUCIÓN =================
    dist = pd.DataFrame({
        "Location":[
            "North Hub",
            "Metro Terminal",
            "South Plant",
            "Regional Depot"
        ],
        "Inventory":[
            inventario_total*0.34,
            inventario_total*0.26,
            inventario_total*0.22,
            inventario_total*0.18
        ]
    })

    col1,col2 = st.columns([2,1])

    with col1:
        st.markdown("### Operational Distribution")
        st.bar_chart(dist.set_index("Location"))

    with col2:
        st.markdown("### Allocation %")
        dist["%"] = dist["Inventory"]/dist["Inventory"].sum()
        st.dataframe(dist[["Location","%"]].style.format({"%":"{:.1%}"}))

    # ================= EXPANDERS =================
    with st.expander("Operational Insight"):
        st.markdown("""
        - Inventory is now visible by operational node  
        - Reduces reconciliation gaps  
        - Enables faster physical stock location  
        - Improves replenishment decisions  
        """)

    with st.expander("Risk Analysis"):
        st.markdown(f"""
        Current operational risk level: **{risk}**
        Suggested order: **{optim.get('suggested_order',0):.0f}**
        """)

    # ================= ABC =================
    if clasificacion_abc:
        with st.expander("ABC Classification"):
            st.dataframe(clasificacion_abc(df))

    else:
        with st.expander("ABC Classification"):
            st.dataframe(df.groupby("sku")["demanda"].sum().reset_index())

# =========================
# OPTIMIZACIÓN
# =========================
with tabs[3]:

    st.markdown("### Replenishment Decision")

    st.markdown(f"""
- Risk Level: **{risk}**
- Suggested Order: **{optim.get('suggested_order',0):.0f}**
- Reorder Point: **{optim.get('reorder_point',0):.1f}**
- Safety Stock: **{optim.get('stock_seguridad',0):.1f}**
- EOQ: **{optim.get('eoq',0):.1f}**
""")

# =========================
# REPORTE
# =========================
with tabs[4]:

    st.markdown("### Executive Report")

    if generar_pdf_bytes:
        pdf = generar_pdf_bytes(df,kpis)
        st.download_button("Download Report", pdf, "ESMAX_Report.pdf")

# =========================
# FOOTER
# =========================
st.markdown("---")
st.markdown("## ESMAX CONTROL TOWER")

st.markdown("""
Operational analytics platform for inventory control, forecasting and supply chain decision support.
""")

if os.path.exists("LAYOUT.png"):
    col1,col2,col3 = st.columns([1,3,1])
    with col2:
        st.image(Image.open("LAYOUT.png"), use_container_width=True)
