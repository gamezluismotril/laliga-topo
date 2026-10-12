import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson
import pickle
import base64
import os

st.set_page_config(
    page_title="La Liga del Topo 26/27",
    page_icon="icono.png" if os.path.exists("icono.png") else "⚽",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .block-container {
        padding-left: 3rem !important;
        padding-right: 3rem !important;
        padding-top: 3rem !important;
        padding-bottom: 1rem !important;
        max-width: 1400px !important;
        margin: 0 auto !important;
    }
    .aviso-top {
        background: linear-gradient(90deg, #fef3c7, #fde68a);
        border: 2px solid #f59e0b;
        border-radius: 8px;
        padding: 0.6rem 1rem;
        margin-bottom: 1rem;
        color: #78350f;
        font-size: 0.8rem;
        text-align: center;
        font-weight: 600;
    }
    .main-header {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 18px;
        padding: 1rem 1.5rem;
        background: linear-gradient(90deg, #1e3a8a 0%, #dc2626 50%, #fbbf24 100%);
        border-radius: 12px;
        margin-bottom: 1.2rem;
        color: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.15);
    }
    .main-header img {
        width: 65px;
        height: 65px;
        border-radius: 50%;
        border: 3px solid white;
        background: white;
        object-fit: cover;
    }
    .main-header h1 {
        font-size: 2rem;
        margin: 0;
        font-weight: 900;
        letter-spacing: 1.5px;
        text-shadow: 2px 2px 6px rgba(0,0,0,0.5);
    }
    .main-header p {
        font-size: 0.85rem;
        margin: 0.2rem 0 0 0;
        opacity: 0.95;
    }
    .section-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #1e3a8a;
        border-left: 4px solid #dc2626;
        padding-left: 10px;
        margin: 1rem 0 0.6rem 0;
    }
    .metric-box {
        background: linear-gradient(135deg, #ffffff, #f8fafc);
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 0.7rem 0.5rem;
        text-align: center;
        transition: all 0.2s;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        min-height: 75px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .metric-box:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        transform: translateY(-2px);
        border-color: #cbd5e1;
    }
    .metric-box .m-label {
        font-size: 0.7rem;
        color: #64748b;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.3px;
        margin-bottom: 0.2rem;
    }
    .metric-box .m-value {
        font-size: 1.4rem;
        font-weight: 800;
        color: #1e293b;
        line-height: 1.1;
    }
    .value-box {
        border-radius: 10px;
        padding: 0.8rem 0.5rem;
        text-align: center;
        min-height: 90px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .value-pos {
        background: linear-gradient(135deg, #dcfce7, #bbf7d0);
        border: 2px solid #16a34a;
    }
    .value-neu {
        background: linear-gradient(135deg, #fef9c3, #fef08a);
        border: 2px solid #ca8a04;
    }
    .value-neg {
        background: linear-gradient(135deg, #fee2e2, #fecaca);
        border: 2px solid #dc2626;
    }
    .value-box .v-label {
        font-size: 0.75rem;
        color: #334155;
        font-weight: 600;
    }
    .value-box .v-num {
        font-size: 1.5rem;
        font-weight: 900;
        color: #0f172a;
        margin: 0.2rem 0;
    }
    .value-box .v-icon {
        font-size: 0.75rem;
        font-weight: 700;
    }
    .match-card {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 25px;
        padding: 1rem 1.5rem;
        background: linear-gradient(135deg, #f1f5f9, #e2e8f0);
        border-radius: 12px;
        margin: 0.8rem 0;
        border: 2px solid #cbd5e1;
    }
    .match-card img {
        width: 60px;
        height: 60px;
        object-fit: contain;
    }
    .match-card .team {
        font-size: 1.3rem;
        font-weight: 800;
        color: #1e293b;
    }
    .match-card .vs {
        font-size: 1.3rem;
        font-weight: 900;
        color: #dc2626;
        padding: 0 8px;
    }
    .goals-line {
        text-align: center;
        font-size: 0.95rem;
        color: #475569;
        margin-bottom: 1rem;
        padding: 0.5rem;
        background: #f8fafc;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
    }
    .footer-legal {
        background: #f1f5f9;
        border-radius: 10px;
        padding: 1.2rem;
        margin-top: 2rem;
        text-align: center;
        border: 1px solid #cbd5e1;
    }
    [data-testid="column"] {
        padding: 0 4px !important;
    }
    .element-container {
        margin-bottom: 0.3rem !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="aviso-top">
    ⚠️ MODELO EDUCATIVO. NO ES CONSEJO FINANCIERO. NO GARANTIZA RESULTADOS. +18.
</div>
""", unsafe_allow_html=True)

try:
    with open("icono.png", "rb") as f:
        icono_b64 = base64.b64encode(f.read()).decode()
    img_html = f'<img src="data:image/png;base64,{icono_b64}" alt="Topo">'
except:
    icono_b64 = ""
    img_html = '<div style="font-size:3rem;">🦫</div>'

st.markdown(f"""
<div class="main-header">
    {img_html}
    <div>
        <h1>LA LIGA DEL TOPO 26/27</h1>
        <p>Dixon-Coles ponderado • Córners • Tarjetas • Árbitros</p>
    </div>
</div>
""", unsafe_allow_html=True)

@st.cache_resource
def cargar_modelos():
    with open("datos/modelo_ponderado.pkl", "rb") as f:
        m_goles = pickle.load(f)
    stats_cf = pd.read_csv("datos/stats_casa_fuera.csv").set_index("equipo")
    arbitros = pd.read_csv("datos/arbitros.csv")
    return m_goles, stats_cf, arbitros

m_goles, stats_cf, arbitros = cargar_modelos()
media_liga_amarillas = arbitros["Media_amarillas"].mean()

p = m_goles["params"]
n = len(m_goles["eq_idx"])
atq_g = p[:n] - p[:n].mean()
dfs_g = p[n:2*n]
ha_g = p[2*n]
eq_g = m_goles["eq_idx"]

def factor_arbitro(nombre):
    if not nombre or nombre not in arbitros["Nombre"].values:
        return 1.0
    return arbitros[arbitros["Nombre"] == nombre]["Media_amarillas"].values[0] / media_liga_amarillas

def predecir(home, away, arbitro=None):
    i, j = eq_g[home], eq_g[away]
    lh = np.exp(atq_g[i] + dfs_g[j] + ha_g)
    la = np.exp(atq_g[j] + dfs_g[i])
    m = np.zeros((10, 10))
    for x in range(10):
        for y in range(10):
            m[x, y] = poisson.pmf(x, lh) * poisson.pmf(y, la)
    ph = np.tril(m, -1).sum()
    pd_ = np.trace(m)
    pa = np.triu(m, 1).sum()
    goles = np.add.outer(np.arange(10), np.arange(10))
    over05 = (m * (goles > 0.5)).sum()
    over15 = (m * (goles > 1.5)).sum()
    over25 = (m * (goles > 2.5)).sum()
    over35 = (m * (goles > 3.5)).sum()
    under25 = 1 - over25
    btts = m[1:, 1:].sum()
    diff = np.arange(10)[:,None] - np.arange(10)[None,:]
    h_m1 = (m * (diff >= 2)).sum()
    h_p1 = (m * (diff <= 1)).sum()
    corners = stats_cf.loc[home, "corners_local"] + stats_cf.loc[away, "corners_visit"] if home in stats_cf.index and away in stats_cf.index else 0
    amarillas = stats_cf.loc[home, "amarillas_local"] + stats_cf.loc[away, "amarillas_visit"] if home in stats_cf.index and away in stats_cf.index else 0
    factor = factor_arbitro(arbitro) if arbitro else 1.0
    amarillas *= factor
    top_scores = []
    for x in range(5):
        for y in range(5):
            top_scores.append((f"{x}-{y}", m[x, y]))
    top_scores.sort(key=lambda t: -t[1])
    return {
        "ph": ph, "pd": pd_, "pa": pa,
        "p1X": ph + pd_, "p12": ph + pa, "pX2": pd_ + pa,
        "over05": over05, "over15": over15, "over25": over25,
        "over35": over35, "under25": under25,
        "btts": btts, "h_m1": h_m1, "h_p1": h_p1,
        "p_c75": 1 - poisson.cdf(7, corners),
        "p_c85": 1 - poisson.cdf(8, corners),
        "p_c95": 1 - poisson.cdf(9, corners),
        "p_c105": 1 - poisson.cdf(10, corners),
        "p_c115": 1 - poisson.cdf(11, corners),
        "p_a25": 1 - poisson.cdf(2, amarillas),
        "p_a35": 1 - poisson.cdf(3, amarillas),
        "p_a45": 1 - poisson.cdf(4, amarillas),
        "p_a55": 1 - poisson.cdf(5, amarillas),
        "corners_esp": corners, "amarillas_esp": amarillas,
        "lh": lh, "la": la, "top_scores": top_scores[:5],
    }

def get_escudo_b64(equipo):
    ruta = f"escudos/{equipo}.png"
    if os.path.exists(ruta):
        with open(ruta, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

def metric_box(label, value):
    st.markdown(f"""
    <div class="metric-box">
        <div class="m-label">{label}</div>
        <div class="m-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)

def value_box(valor, nombre):
    color = "value-pos" if valor > 0.05 else "value-neu" if valor > 0 else "value-neg"
    icono = "✅ APOSTAR" if valor > 0.05 else "⚠️ MARGINAL" if valor > 0 else "❌ NO"
    st.markdown(f"""
    <div class="value-box {color}">
        <div class="v-label">{nombre}</div>
        <div class="v-num">{valor*100:+.1f}%</div>
        <div class="v-icon">{icono}</div>
    </div>
    """, unsafe_allow_html=True)

equipos = sorted(stats_cf.index.tolist())

st.markdown('<div class="section-title">🎯 Selecciona el partido</div>', unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
with col1:
    home = st.selectbox("🏠 Equipo local", equipos, index=equipos.index("Real Madrid") if "Real Madrid" in equipos else 0)
with col2:
    away = st.selectbox("✈️ Equipo visitante", equipos, index=equipos.index("Sevilla") if "Sevilla" in equipos else 1)
with col3:
    arb = st.selectbox("👨‍⚖️ Árbitro", ["Sin árbitro"] + sorted(arbitros["Nombre"].tolist()))

arb_final = arb if arb != "Sin árbitro" else None
r = predecir(home, away, arb_final)

margen = 1.08
sug_h = round(1 / (r['ph'] * margen), 2) if r['ph'] > 0.05 else 20.0
sug_d = round(1 / (r['pd'] * margen), 2) if r['pd'] > 0.05 else 20.0
sug_a = round(1 / (r['pa'] * margen), 2) if r['pa'] > 0.05 else 20.0
sug_o25 = round(1 / (r['over25'] * margen), 2) if r['over25'] > 0.05 else 20.0

st.markdown('<div class="section-title">💰 Cuotas reales de tu casa</div>', unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)
cuota_h = c1.number_input(f"Gana {home}", min_value=1.01, max_value=1000.0, value=float(sug_h), step=0.05)
cuota_d = c2.number_input("Empate", min_value=1.01, max_value=1000.0, value=float(sug_d), step=0.05)
cuota_a = c3.number_input(f"Gana {away}", min_value=1.01, max_value=1000.0, value=float(sug_a), step=0.05)
cuota_o25 = c4.number_input("Over 2.5", min_value=1.01, max_value=1000.0, value=float(sug_o25), step=0.05)

if st.button("🔮 PREDECIR", type="primary", use_container_width=True):
    escudo_home = get_escudo_b64(home)
    escudo_away = get_escudo_b64(away)
    img_home = f'<img src="data:image/png;base64,{escudo_home}">' if escudo_home else ""
    img_away = f'<img src="data:image/png;base64,{escudo_away}">' if escudo_away else ""
    
    st.markdown(f"""
    <div class="match-card">
        {img_home}
        <div class="team">{home}</div>
        <div class="vs">VS</div>
        <div class="team">{away}</div>
        {img_away}
    </div>
    <div class="goals-line">
        ⚽ Goles esperados: <b>{home} {r['lh']:.2f}</b> — <b>{away} {r['la']:.2f}</b>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="section-title">🎯 Resultado 1X2</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: metric_box(f"Gana {home}", f"{r['ph']*100:.1f}%")
    with c2: metric_box("Empate", f"{r['pd']*100:.1f}%")
    with c3: metric_box(f"Gana {away}", f"{r['pa']*100:.1f}%")
    
    st.markdown('<div class="section-title">🛡️ Doble oportunidad</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: metric_box("1X", f"{r['p1X']*100:.1f}%")
    with c2: metric_box("12", f"{r['p12']*100:.1f}%")
    with c3: metric_box("X2", f"{r['pX2']*100:.1f}%")
    
    st.markdown('<div class="section-title">⚽ Goles</div>', unsafe_allow_html=True)
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1: metric_box("Over 0.5", f"{r['over05']*100:.1f}%")
    with c2: metric_box("Over 1.5", f"{r['over15']*100:.1f}%")
    with c3: metric_box("Over 2.5", f"{r['over25']*100:.1f}%")
    with c4: metric_box("Over 3.5", f"{r['over35']*100:.1f}%")
    with c5: metric_box("Under 2.5", f"{r['under25']*100:.1f}%")
    with c6: metric_box("BTTS", f"{r['btts']*100:.1f}%")
    
    st.markdown('<div class="section-title">⚖️ Hándicap asiático</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1: metric_box(f"{home} -1", f"{r['h_m1']*100:.1f}%")
    with c2: metric_box(f"{away} +1", f"{r['h_p1']*100:.1f}%")
    
    st.markdown('<div class="section-title">🚩 Córners</div>', unsafe_allow_html=True)
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1: metric_box("Esperados", f"{r['corners_esp']:.1f}")
    with c2: metric_box("Over 7.5", f"{r['p_c75']*100:.1f}%")
    with c3: metric_box("Over 8.5", f"{r['p_c85']*100:.1f}%")
    with c4: metric_box("Over 9.5", f"{r['p_c95']*100:.1f}%")
    with c5: metric_box("Over 10.5", f"{r['p_c105']*100:.1f}%")
    with c6: metric_box("Over 11.5", f"{r['p_c115']*100:.1f}%")
    
    st.markdown('<div class="section-title">🟨 Amarillas</div>', unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: metric_box("Esperadas", f"{r['amarillas_esp']:.1f}")
    with c2: metric_box("Over 2.5", f"{r['p_a25']*100:.1f}%")
    with c3: metric_box("Over 3.5", f"{r['p_a35']*100:.1f}%")
    with c4: metric_box("Over 4.5", f"{r['p_a45']*100:.1f}%")
    with c5: metric_box("Over 5.5", f"{r['p_a55']*100:.1f}%")
    
    st.markdown('<div class="section-title">🎲 Marcadores más probables</div>', unsafe_allow_html=True)
    cols = st.columns(5)
    for i, (score, prob) in enumerate(r["top_scores"]):
        with cols[i]: metric_box(f"Resultado {score}", f"{prob*100:.1f}%")
    
    st.markdown('<div class="section-title">💎 VALUE — ¿Dónde apostar?</div>', unsafe_allow_html=True)
    value_h = (r['ph'] * cuota_h) - 1
    value_d = (r['pd'] * cuota_d) - 1
    value_a = (r['pa'] * cuota_a) - 1
    value_o25 = (r['over25'] * cuota_o25) - 1
    
    c1, c2, c3, c4 = st.columns(4)
    with c1: value_box(value_h, f"Gana {home}")
    with c2: value_box(value_d, "Empate")
    with c3: value_box(value_a, f"Gana {away}")
    with c4: value_box(value_o25, "Over 2.5")
    
    st.markdown('<div class="section-title">📋 Cuotas justas del modelo</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1: metric_box(f"Gana {home}", f"{1/r['ph']:.2f}" if r['ph'] > 0 else "-")
    with c2: metric_box("Empate", f"{1/r['pd']:.2f}" if r['pd'] > 0 else "-")
    with c3: metric_box(f"Gana {away}", f"{1/r['pa']:.2f}" if r['pa'] > 0 else "-")
    with c4: metric_box("Over 2.5", f"{1/r['over25']:.2f}" if r['over25'] > 0 else "-")

st.markdown("---")

if icono_b64:
    st.markdown(f"""
    <div style="text-align:center;padding:1rem 0;">
        <img src="data:image/png;base64,{icono_b64}" style="width:70px;height:70px;border-radius:50%;border:2px solid #1e3a8a;background:white;object-fit:cover;margin-bottom:0.5rem;">
        <div style="color:#64748b;font-size:0.8rem;">
            ⚠️ Sistema educativo. No garantiza resultados. Apuesta con responsabilidad.
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div class="footer-legal">
    <div style="font-weight:800;color:#dc2626;margin-bottom:0.5rem;font-size:1rem;">⚠️ AVISO LEGAL</div>
    <div style="color:#475569;font-size:0.78rem;line-height:1.6;">
        <b>+18.</b> Este sistema es <b>educativo</b> y no garantiza resultados.<br>
        No es consejo financiero. Nunca apuestes más de lo que puedas perder.<br>
        Juego responsable: <a href="https://www.jugarbien.es" target="_blank" style="color:#1e3a8a;">jugarbien.es</a>
    </div>
</div>
""", unsafe_allow_html=True)