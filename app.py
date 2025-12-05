import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.graph_objects as go
import time

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Futbol Asistanı Pro", page_icon="⚽", layout="wide")

# --- MODERN TASARIM ---
st.markdown("""
<style>
    .stApp { background-color: #0E1117; }
    h1 { color: #00CC96 !important; text-align: center; font-family: 'Arial Black', sans-serif; }
    h2, h3 { color: white !important; }
    .stButton>button { 
        background: linear-gradient(to right, #00CC96, #00b887); 
        color: white; 
        width: 100%; 
        border-radius: 12px; 
        height: 55px; 
        font-size: 20px; 
        border: none;
        box-shadow: 0px 4px 15px rgba(0, 204, 150, 0.4);
    }
    .stButton>button:hover { transform: scale(1.02); }
</style>
""", unsafe_allow_html=True)

# --- BAŞLIK ---
st.title("🦁 FUTBOL ASİSTANI PRO")
st.markdown("<p style='text-align: center; color: gray;'>Yapay Zeka Destekli Analiz Platformu</p>", unsafe_allow_html=True)

# --- 1. CANLI SKOR (GİZLENEBİLİR) ---
with st.expander("🔴 CANLI MAÇLARI GÖSTER (Livescore)", expanded=False):
    components.html(
        """<iframe src="https://www.livescore.bz" width="100%" height="600" frameborder="0" style="background-color: white; border-radius: 8px;"></iframe>""",
        height=600, scrolling=True
    )

st.divider()

# --- 2. ANALİZ VERİ MOTORU ---
takim_duzeltme = {
    "Fenerbahce": "Fenerbahçe", "Galatasaray": "Galatasaray", "Besiktas": "Beşiktaş",
    "Trabzonspor": "Trabzonspor", "Buyuksehyr": "Başakşehir FK", "Man City": "Manchester City",
    "Man United": "Manchester United", "Liverpool": "Liverpool", "Arsenal": "Arsenal", "Chelsea": "Chelsea"
}

@st.cache_data(ttl=3600)
def veri_getir(lig_kodu):
    # HATA ÇIKARAN SATIRI BÖLDÜK (ARTIK GÜVENLİ)
    if lig_kodu == "TR":
        url = "https://www.football-data.co.uk/mmz4281/2425/T1.csv"
    else:
        url = "https
