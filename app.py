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
    .stButton>button { width: 100%; border-radius: 20px; font-weight: bold; background-color: #00CC96; color: white; }
    /* İframe çerçevesini güzelleştir */
    iframe { border-radius: 10px; border: 2px solid #333; }
</style>
""", unsafe_allow_html=True)

# --- 1. CANLI SKOR MODÜLÜ (HIZLI VERSİYON) ---
st.title("🦁 FUTBOL ASİSTANI")
st.caption("🚀 Canlı Skorlar ve Yapay Zeka Analizi")

with st.expander("🔴 CANLI MAÇLARI GÖSTER (Hızlı)", expanded=True):
    # Scorebat yerine LiveScore.bz kullanıyoruz (Çok daha hızlıdır)
    components.html(
        """
        <iframe src="https://www.livescore.bz" 
        width="100%" height="600" 
        frameborder="0" 
        style="background-color: white;">
        </iframe>
        """,
        height=610,
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
