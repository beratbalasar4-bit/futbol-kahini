import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.graph_objects as go
import time

# --- 1. SAYFA VE İKON AYARLARI (LOGOLU) ---
# page_icon kısmına bir futbol topu veya aslan emojisi yerine link de koyabiliriz ama emoji daha hızlı açılır.
st.set_page_config(page_title="Futbol Kahini Pro", page_icon="🦁", layout="wide")

# --- TASARIM (CSS) ---
st.markdown("""
<style>
    .stApp { background-color: #0E1117; }
    h1 { color: #00CC96 !important; text-align: center; font-family: 'Arial Black', sans-serif; }
    .kupon-karti { background-color: #1F2937; padding: 20px; border-radius: 15px; border-left: 10px solid #00CC96; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
    .stButton>button { 
        background: linear-gradient(to right, #00CC96, #00b887); 
        color: white; width: 100%; border-radius: 12px; height: 55px; font-size: 20px; border: none; font-weight: bold;
    }
    .stButton>button:hover { transform: scale(1.02); transition: 0.3s; }
    /* Yan Menü Düzeni */
    [data-testid="stSidebar"] { background-color: #111; }
</style>
""", unsafe_allow_html=True)

# --- YAN MENÜ (LOGO VE SOSYAL MEDYA) ---
with st.sidebar:
    # BURAYA LOGO GELİYOR
    st.image("https://cdn-icons-png.flaticon.com/512/3233/3233496.png", width=120) 
    st.markdown("<h2 style='text-align: center; color: white;'>FUTBOL KAHİNİ</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    st.info("💡 **İPUCU:** Sol üstteki menüden lig seçimi yapabilirsin.")
    
    # TELEGRAM / GRUP BUTONU (PARA KAZANMA ADIMI)
    st.markdown("### 💎 VIP GRUP")
    st.link_button("👉 Telegram'a Katıl", "https://t.me/berat_futbol_kahini") # Buraya kendi linkini koyarsın
    st.caption("Banko kuponlar ve özel analizler için grubumuza katıl.")

# --- BAŞLIK ---
st.title("🌍 FUTBOL KAHİNİ GLOBAL")
st.markdown("<p style='text-align: center; color: gray;'>Yapay Zeka Destekli Profesyonel Analiz Merkezi</p>", unsafe_allow_html=True)

# --- CANLI SKOR ---
with st.expander("🔴 CANLI MAÇLARI GÖSTER (Livescore)", expanded=False):
    components.html(
        """<iframe src="https://www.livescore.bz" width="100%" height="600" frameborder="0" style="background-color: white; border-radius: 8px;"></iframe>""",
        height=600, scrolling=True
    )

st.divider()

# --- VERİ MOTORU ---
lig_kodlari = {
    "🇹🇷 Türkiye Süper Lig": "T1.csv",
    "🇬🇧 İngiltere Premier Lig": "E0.csv",
    "🇪🇸 İspanya La Liga": "SP1.csv",
    "🇩🇪 Almanya Bundesliga": "D1.csv",
    "🇮🇹 İtalya Serie A": "I1.csv",
    "🇫🇷 Fransa Ligue 1": "F1.csv",
    "🇳🇱 Hollanda Eredivisie": "N1.csv"
}

takim_duzeltme = {
    "Fenerbahce": "Fenerbahçe", "Galatasaray": "Galatasaray", "Besiktas": "Beşiktaş", "Trabzonspor": "Trabzonspor",
    "Buyuksehyr": "Başakşehir FK", "Man City": "Manchester City", "Man United": "Manchester United",
    "Real Madrid": "Real Madrid", "Barcelona": "Barcelona", "Bayern Munich": "Bayern Münih",
    "Paris SG": "PSG", "Inter": "Inter Milan", "Milan": "AC Milan", "Juventus": "Juventus"
}

@st.cache_data(ttl=3600)
def veri_getir(secilen_lig):
    dosya_adi = lig_kodlari[secilen_lig]
    # URL Parçalama
    ana_url = "https://www.football-data.co.uk/mmz4281/2425/"
    full_url = ana_url + dosya_adi
    
    try:
        df = pd.read_csv(full_url)
        df = df.dropna(subset=['FTR'])
        df['HomeTeam'] = df['HomeTeam'].replace(takim_duzeltme)
        df['AwayTeam'] = df['AwayTeam'].replace(takim_duzeltme)
        return df
    except: return None

# --- ANALİZ EKRANI ---
st.subheader("🏆 DETAYLI ANALİZ MASASI")

secilen_lig = st.selectbox("Ligi Seçiniz:", list(lig_kodlari.keys()))
df = veri_getir(secilen_lig)

if df is not None:
    takimlar = sorted(df['HomeTeam'].unique())
    col1, col2 = st.columns(2)
    with col1: ev = st.selectbox("Ev Sahibi", takimlar)
    with col2: dep = st.selectbox("Deplasman", takimlar, index=1)

    st.write("")
    
    if st.button("DETAYLI KUPON OLUŞTUR 🚀"):
        with st.spinner('Yapay Zeka Hesaplıyor...'):
            time.sleep(0.8)
            
            ev_stats = df[df['HomeTeam'] == ev]
            dep_stats = df[df['AwayTeam'] == dep]

            if len(ev_stats) > 0 and len(dep_stats) > 0:
                # Hesaplamalar
                ev_gol_ort = (ev_stats['FTHG'].mean() + ev_stats['FTAG'].mean()) / 2
                dep_gol_ort = (dep_stats['FTHG'].mean() + dep_stats['FTAG'].mean()) / 2
                mac_gol_beklentisi = (ev_gol_ort + dep_gol_ort)
                
                # Korner (Varsayılan veya Gerçek)
                if 'HC' in df.columns:
                    ev_korner = ev_stats['HC'].mean() + ev_stats['AC'].mean()
                    dep_korner = dep_stats['HC'].mean() + dep_stats['AC'].mean()
                    toplam_korner = (ev_korner + dep_korner) / 2
                else: toplam_korner = 9.0
                
                # Kart
                if 'HY' in df.columns:
                    ev_kart = ev_stats['HY'].mean() + ev_stats['AY'].mean()
                    dep_kart = dep_stats['HY'].mean() + dep_stats['AY'].mean()
                    toplam_kart = (ev_kart + dep_kart) / 2
                else: toplam_kart = 4.0

                # İbre
                ev_puan = (ev_stats['FTHG'].mean() * 40) - (ev_stats['FTAG'].mean() * 20)
                dep_puan = (dep_stats['FTAG'].mean() * 40) - (dep_stats['FTHG'].mean() * 20)
                fark = ev_puan - dep_puan
                ibre = 50 + (fark / 1.8)
                ibre = max(10, min(90, ibre))

                # --- SONUÇ KARTI ---
                st.markdown(f"""
                <div class="kupon-karti">
                    <h2 style="text-align:center; color:white;">MAÇ RAPORU</h2>
                    <h3 style="text-align:center; color:#00CC96;">{ev} vs {dep}</h3>
                    <hr style="border-color:gray;">
                </div>
                """, unsafe_allow_html=True)

                k1, k2, k3, k4 = st.columns(4)
                with k1:
                    st.info("🏆 MAÇ SONUCU")
                    if ibre > 60: st.markdown(f"**{ev}** (MS 1)")
                    elif ibre < 40: st.markdown(f"**{dep}** (MS 2)")
                    else: st.markdown("**BERABERLİK** (MS 0)")
                with k2:
                    st.warning("⚽ GOL")
                    if mac_gol_beklentisi > 2.6: st.markdown("**2.5 ÜST**")
                    else: st.markdown("**2.5 ALT**")
                with k3:
                    st.success("⛳ KORNER")
                    st.markdown(f"Tahmin: **{toplam_korner:.1f}**")
                with k4:
                    st.error("🟨 KART")
                    st.markdown(f"Ort: **{toplam_kart:.1f}**")

                st.divider()

                # Grafikler
                g1, g2 = st.columns([2, 1])
                with g1:
                    categories = ['Hücum', 'Defans', 'Korner', 'Sertlik', 'Form']
                    fig = go.Figure()
                    fig.add_trace(go.Scatterpolar(r=[ev_puan, 80, toplam_korner*8, toplam_kart*15, ev_puan], theta=categories, fill='toself', name=ev, line_color='#00CC96'))
                    fig.add_trace(go.Scatterpolar(r=[dep_puan, 60, toplam_korner*7, toplam_kart*15, dep_puan], theta=categories, fill='toself', name=dep, line_color='#FF4B4B'))
                    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), template="plotly_dark", title="Detaylı Analiz", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig, use_container_width=True)
                with g2:
                    fig_gauge = go.Figure(go.Indicator(
                        mode = "gauge+number", value = ibre, title = {'text': "Kazanma Şansı %"},
                        gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': "white"}, 'steps': [{'range': [0, 45], 'color': "#FF4B4B"}, {'range': [45, 55], 'color': "gray"}, {'range': [55, 100], 'color': "#00CC96"}]}
                    ))
                    fig_gauge.update_layout(height=300, margin=dict(t=50,b=20,l=20,r=20), paper_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig_gauge, use_container_width=True)
            else: st.error("Veri yetersiz.")
else: st.info("Veri sunucusu bekleniyor...")

# --- FOOTER (ALT BİLGİ) ---
st.markdown("---")
st.markdown("<p style='text-align: center; color: gray; font-size: 12px;'>© 2024 Futbol Kahini - Bu bir yapay zeka analiz aracıdır. Bahis tavsiyesi değildir.</p>", unsafe_allow_html=True)
