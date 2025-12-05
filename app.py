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
    # --- HATA ÇÖZÜMÜ (KISA PARÇALAR) ---
    # Linki bilerek kisa kisa yaziyoruz ki kopyalarken bozulmasin
    site = "https://www.football-data.co.uk"
    klasor = "/mmz4281/2425/"
    
    if lig_kodu == "TR":
        dosya = "T1.csv"
    else:
        dosya = "E0.csv"
    
    # Parcalari birlestir
    url = site + klasor + dosya
    
    try:
        df = pd.read_csv(url)
        df = df.dropna(subset=['FTR'])
        df['HomeTeam'] = df['HomeTeam'].replace(takim_duzeltme)
        df['AwayTeam'] = df['AwayTeam'].replace(takim_duzeltme)
        return df
    except: return None

# --- ARAYÜZ ---
st.subheader("🧠 YAPAY ZEKA KAHİNİ")

lig_secimi = st.selectbox("Ligi Seçiniz:", ["Türkiye Süper Lig", "İngiltere Premier Lig"])

if lig_secimi == "Türkiye Süper Lig":
    df = veri_getir("TR")
else:
    df = veri_getir("EN")

if df is not None:
    takimlar = sorted(df['HomeTeam'].unique())
    col1, col2 = st.columns(2)
    with col1: ev = st.selectbox("Ev Sahibi", takimlar)
    with col2: dep = st.selectbox("Deplasman", takimlar, index=1)

    st.write("")
    
    if st.button("MAÇI ANALİZ ET 🚀"):
        with st.spinner('Veriler Taranıyor...'):
            time.sleep(0.5)
            
            ev_stats = df[df['HomeTeam'] == ev]
            dep_stats = df[df['AwayTeam'] == dep]

            if len(ev_stats) > 0:
                # Güç Formülü
                ev_guc = (ev_stats['FTHG'].mean() * 35) + 25
                ev_def = 100 - (ev_stats['FTAG'].mean() * 30)
                dep_guc = (dep_stats['FTAG'].mean() * 35) + 25
                dep_def = 100 - (dep_stats['FTHG'].mean() * 30)
                
                # İbre Hesabı
                ev_toplam = ev_guc + ev_def
                dep_toplam = dep_guc + dep_def
                fark = ev_toplam - dep_toplam
                ibre = 50 + (fark / 1.5)
                ibre = max(5, min(95, ibre))

                # --- GRAFİKLER ---
                categories = ['Hücum', 'Defans', 'Form', 'Şut', 'Motivasyon']
                fig = go.Figure()
                fig.add_trace(go.Scatterpolar(r=[ev_guc, ev_def, ev_guc-5, ev_guc+5, ev_guc], theta=categories, fill='toself', name=ev, line_color='#00CC96'))
                fig.add_trace(go.Scatterpolar(r=[dep_guc, dep_def, dep_guc-5, dep_guc+5, dep_guc], theta=categories, fill='toself', name=dep, line_color='#FF4B4B'))
                fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), template="plotly_dark", title="Güç Analizi")

                fig_gauge = go.Figure(go.Indicator(
                    mode = "gauge+number", value = ibre,
                    title = {'text': "Kazanma İhtimali (%)"},
                    gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': "white"}, 'steps': [{'range': [0, 45], 'color': "#FF4B4B"}, {'range': [45, 55], 'color': "gray"}, {'range': [55, 100], 'color': "#00CC96"}]}
                ))
                fig_gauge.update_layout(height=250, margin=dict(t=30,b=10,l=20,r=20))

                c1, c2 = st.columns(2)
                with c1: st.plotly_chart(fig, use_container_width=True)
                with c2: st.plotly_chart(fig_gauge, use_container_width=True)

                if ibre > 55: st.success(f"✅ **BANKO:** {ev} kazanmaya yakın!")
                elif ibre < 45: st.error(f"⚠️ **SÜRPRİZ:** {dep} kazanabilir!")
                else: st.warning("💣 **RİSK:** Beraberlik ihtimali yüksek.")
            else:
                st.error("Veri yok.")
else:
    st.warning("Veriler yükleniyor...")
