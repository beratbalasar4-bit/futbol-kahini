import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import time

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="AI Futbol Asistanı", page_icon="⚽", layout="wide")

# --- CSS (Tasarım) ---
st.markdown("""
<style>
    .stApp { background-color: #0E1117; }
    h1 { color: #00CC96 !important; text-align: center; }
    .stButton>button { background-color: #00CC96; color: white; width: 100%; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# --- BAŞLIK ---
st.title("🦁 FUTBOL ASİSTANI (GÜVENLİ MOD)")
st.caption("Eğer bu yazıyı görüyorsan sistem çalışıyor demektir.")
st.divider()

# --- VERİ ÇEKME ---
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

# --- SEÇİM EKRANI ---
st.subheader("1. Ayarlar")
col_lig = st.columns(1)[0]
lig_secimi = col_lig.selectbox("Ligi Seç:", ["Türkiye Süper Lig", "İngiltere Premier Lig"])

if lig_secimi == "Türkiye Süper Lig":
    df = veri_getir("TR")
else:
    df = veri_getir("EN")

if df is not None:
    takimlar = sorted(df['HomeTeam'].unique())
    
    col1, col2 = st.columns(2)
    with col1:
        ev = st.selectbox("Ev Sahibi", takimlar)
    with col2:
        dep = st.selectbox("Deplasman", takimlar, index=1)

    st.write("") # Boşluk
    if st.button("ANALİZ ET 🚀"):
        with st.spinner('Hesaplanıyor...'):
            time.sleep(0.5)
            
            ev_stats = df[df['HomeTeam'] == ev]
            dep_stats = df[df['AwayTeam'] == dep]

            if len(ev_stats) > 0:
                ev_att = (ev_stats['FTHG'].mean() * 35) + 20
                dep_att = (dep_stats['FTAG'].mean() * 35) + 20
                
                # Basit Sonuç Kartları
                c1, c2 = st.columns(2)
                c1.metric(f"{ev} Gücü", f"{ev_att:.0f}")
                c2.metric(f"{dep} Gücü", f"{dep_att:.0f}")
                
                # Grafik
                categories = ['Hücum', 'Defans', 'Form', 'Şut', 'Beklenti']
                fig = go.Figure()
                fig.add_trace(go.Scatterpolar(r=[ev_att, 80, 70, 60, ev_att], theta=categories, fill='toself', name=ev))
                fig.add_trace(go.Scatterpolar(r=[dep_att, 60, 50, 40, dep_att], theta=categories, fill='toself', name=dep))
                fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), template="plotly_dark")
                st.plotly_chart(fig, use_container_width=True)

            else:
                st.error("Veri yok.")
else:
    st.error("⚠️ Veri sunucusuna bağlanılamadı! (İnternet bağlantını kontrol et)")
