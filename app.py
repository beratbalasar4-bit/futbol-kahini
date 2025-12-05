import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.graph_objects as go

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="AI Futbol Asistanı", page_icon="⚽", layout="wide")

# --- MODERN TASARIM (CSS) ---
st.markdown("""
<style>
    .stApp { background-color: #0E1117; }
    h1, h2, h3 { color: #00CC96 !important; font-family: 'Arial', sans-serif; }
    .stButton>button { width: 100%; border-radius: 20px; font-weight: bold; }
    .css-1v0mbdj { margin-top: -50px; }
</style>
""", unsafe_allow_html=True)

# --- 1. CANLI SKOR MODÜLÜ (MAÇKOLİK KISMI) ---
st.title("🦁 FUTBOL ASİSTANI & LIVE")
st.caption("Canlı Skorlar ve Yapay Zeka Destekli Analiz Platformu")

with st.expander("🔴 CANLI MAÇ MERKEZİ (Görmek için tıkla)", expanded=True):
    components.html(
        """
        <iframe src="https://www.scorebat.com/embed/livescore/" 
        frameborder="0" width="100%" height="400" 
        style="width:100%;height:400px;overflow:hidden;display:block;" 
        allow="autoplay; fullscreen" class="_scorebat_"></iframe>
        <script>(function(d, s, id) { var js, fjs = d.getElementsByTagName(s)[0]; if (d.getElementById(id)) return; js = d.createElement(s); js.id = id; js.src = 'https://www.scorebat.com/embed/embed.js?v=arrv'; fjs.parentNode.insertBefore(js, fjs); }(document, 'script', 'scorebat-jssdk'));</script>
        """,
        height=410,
        scrolling=True
    )

st.divider()

# --- 2. YAPAY ZEKA KAHİNİ (ANALİZ KISMI) ---
st.header("🧠 YAPAY ZEKA ANALİZİ")

# İsim Düzeltme
takim_duzeltme = {
    "Fenerbahce": "Fenerbahçe", "Galatasaray": "Galatasaray", "Besiktas": "Beşiktaş",
    "Trabzonspor": "Trabzonspor", "Buyuksehyr": "Başakşehir FK", "Man City": "Manchester City",
    "Man United": "Manchester United", "Liverpool": "Liverpool", "Arsenal": "Arsenal", "Chelsea": "Chelsea"
}

@st.cache_data(ttl=3600)
def veri_getir(lig_kodu):
    url = "https://www.football-data.co.uk/mmz4281/2425/T1.csv" if lig_kodu == "TR" else "https://www.football-data.co.uk/mmz4281/2425/E0.csv"
    try:
        df = pd.read_csv(url)
        df = df.dropna(subset=['FTR'])
        df['HomeTeam'] = df['HomeTeam'].replace(takim_duzeltme)
        df['AwayTeam'] = df['AwayTeam'].replace(takim_duzeltme)
        return df
    except: return None

# Yan Menü
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2503/2503509.png", width=100)
    st.markdown("### ⚙️ Analiz Ayarları")
    lig = st.selectbox("Ligi Seç:", ("Türkiye Süper Lig", "İngiltere Premier Lig"))
    
    df = veri_getir("TR" if lig == "Türkiye Süper Lig" else "EN")
    
    if df is not None:
        takimlar = sorted(df['HomeTeam'].unique())
        ev = st.selectbox("Ev Sahibi", takimlar)
        dep = st.selectbox("Deplasman", takimlar, index=1)
        analiz_baslat = st.button("ANALİZ ET ➤", type="primary")
    else:
        st.error("Veri alınamadı.")

# Analiz Ekranı
if df is not None and analiz_baslat:
    ev_stats = df[df['HomeTeam'] == ev]
    dep_stats = df[df['AwayTeam'] == dep]

    if len(ev_stats) > 0 and len(dep_stats) > 0:
        # Puanlama
        ev_att = min(99, (ev_stats['FTHG'].mean() * 35) + 15)
        ev_def = min(99, 100 - (ev_stats['FTAG'].mean() * 35))
        dep_att = min(99, (dep_stats['FTAG'].mean() * 35) + 15)
        dep_def = min(99, 100 - (dep_stats['FTHG'].mean() * 35))

        # --- A. RADAR GRAFİĞİ ---
        categories = ['Hücum', 'Defans', 'Form', 'Şut Gücü', 'Gol Beklentisi']
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(r=[ev_att, ev_def, ev_att-5, ev_att+5, ev_att], theta=categories, fill='toself', name=ev, line_color='#00CC96'))
        fig.add_trace(go.Scatterpolar(r=[dep_att, dep_def, dep_att-5, dep_att+5, dep_att], theta=categories, fill='toself', name=dep, line_color='#FF4B4B'))
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), template="plotly_dark", title="Güç Analizi", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')

        # --- B. İBRE GRAFİĞİ ---
        fark = (ev_att + ev_def) - (dep_att + dep_def)
        ibre = 50 + (fark / 2)
        ibre = max(10, min(90, ibre)) # Sınırla

        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number", value = ibre,
            title = {'text': "Galibiyet İbresi"},
            gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': "white"}, 'steps': [{'range': [0, 40], 'color': "#FF4B4B"}, {'range': [40, 60], 'color': "gray"}, {'range': [60, 100], 'color': "#00CC96"}]}
        ))
        fig_gauge.update_layout(height=300, margin=dict(t=50,b=20,l=20,r=20), paper_bgcolor='rgba(0,0,0,0)')

        # GÖRSELLEŞTİRME
        c1, c2 = st.columns([1.5, 1])
        with c1: st.plotly_chart(fig, use_container_width=True)
        with c2: 
            st.plotly_chart(fig_gauge, use_container_width=True)
            if ibre > 60: st.success(f"🏆 Favori: **{ev}**")
            elif ibre < 40: st.error(f"🏆 Favori: **{dep}**")
            else: st.warning("⚖️ Maç Ortada!")

    else:
        st.warning("Yetersiz Veri.")
else:
    st.info("👈 Soldan takım seçip analizi başlatabilirsin.")
