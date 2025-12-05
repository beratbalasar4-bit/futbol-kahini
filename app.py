import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.graph_objects as go
import time

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Futbol Asistanı Pro", page_icon="⚽", layout="wide")

# --- TASARIM ---
st.markdown("""
<style>
    .stApp { background-color: #0E1117; }
    h1 { color: #00CC96 !important; text-align: center; font-family: 'Arial Black', sans-serif; }
    .stButton>button { 
        background: linear-gradient(to right, #00CC96, #00b887); 
        color: white; width: 100%; border-radius: 12px; height: 55px; font-size: 20px; border: none;
    }
</style>
""", unsafe_allow_html=True)

# --- BAŞLIK ---
st.title("🦁 FUTBOL ASİSTANI PRO")

# --- 1. CANLI SKOR ---
with st.expander("🔴 CANLI MAÇLARI GÖSTER (Livescore)", expanded=False):
    components.html(
        """<iframe src="https://www.livescore.bz" width="100%" height="600" frameborder="0" style="background-color: white; border-radius: 8px;"></iframe>""",
        height=600, scrolling=True
    )

st.divider()

# --- 2. VERİ MOTORU ---
takim_duzeltme = {
    "Fenerbahce": "Fenerbahçe", "Galatasaray": "Galatasaray", "Besiktas": "Beşiktaş",
    "Trabzonspor": "Trabzonspor", "Buyuksehyr": "Başakşehir FK", "Man City": "Manchester City",
    "Man United": "Manchester United", "Liverpool": "Liverpool", "Arsenal": "Arsenal", "Chelsea": "Chelsea"
}

@st.cache_data(ttl=3600)
def veri_getir(lig_kodu):
    # --- HATA ÇÖZÜMÜ BURADA ---
    # Uzun linki parçalara böldük, artık hata vermez.
    ana_link = "https
