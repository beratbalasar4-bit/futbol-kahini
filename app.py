import streamlit as st
import streamlit.components.v1 as components
import pandas as pd

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Futbol Kahini Canlı", page_icon="⚽", layout="wide")

# --- CSS İLE GÖRSEL DÜZENLEME ---
st.markdown("""
<style>
    .main { background-color: #0e1117; }
    h1 { color: #FEEB77 !important; text-align: center; }
    .stSelectbox label { color: white !important; font-size: 18px; }
</style>
""", unsafe_allow_html=True)

# --- BAŞLIK ---
st.title("🦁 FUTBOL KÂHİNİ & CANLI SKOR")
st.write("---")

# --- 1. MAÇKOLİK GİBİ CANLI SKOR EKRANI (WIDGET) ---
# Buraya hazır bir iframe gömüyoruz. Kod yazmadan canlı maçları gösterir.
st.subheader("🔴 CANLI MAÇ MERKEZİ")
components.html(
    """
    <iframe src="https://www.scorebat.com/embed/livescore/" 
    frameborder="0" 
    width="100%" 
    height="440" 
    allowfullscreen 
    allow="autoplay; fullscreen" 
    style="width:100%;height:440px;overflow:hidden;display:block;" 
    class="_scorebat_">
    </iframe>
    <script>(function(d, s, id) { var js, fjs = d.getElementsByTagName(s)[0]; if (d.getElementById(id)) return; js = d.createElement(s); js.id = id; js.src = 'https://www.scorebat.com/embed/embed.js?v=arrv'; fjs.parentNode.insertBefore(js, fjs); }(document, 'script', 'scorebat-jssdk'));</script>
    """,
    height=450,
    scrolling=True
)

st.write("---")
st.subheader("🤖 YAPAY ZEKA KAHİNİ (Detaylı Analiz)")

# --- 2. SENİN YAPAY ZEKA KODLARIN BURADA ---
takim_duzeltme = {
    "Fenerbahce": "Fenerbahçe", "Galatasaray": "Galatasaray", "Besiktas": "Beşiktaş",
    "Trabzonspor": "Trabzonspor", "Buyuksehyr": "Başakşehir FK", "Ankaragucu": "Ankaragücü",
    "Man City": "Manchester City", "Man United": "Manchester United", "Liverpool": "Liverpool",
    "Arsenal": "Arsenal", "Chelsea": "Chelsea"
}

@st.cache_data(ttl=3600)
def veri_getir(lig_kodu):
    url = ""
    if lig_kodu == "TR": url = "https://www.football-data.co.uk/mmz4281/2425/T1.csv"
    elif lig_kodu == "EN": url = "https://www.football-data.co.uk/mmz4281/2425/E0.csv"
    try:
        df = pd.read_csv(url)
        df = df.dropna(subset=['FTR'])
        df['HomeTeam'] = df['HomeTeam'].replace(takim_duzeltme)
        df['AwayTeam'] = df['AwayTeam'].replace(takim_duzeltme)
        return df
    except: return None

# --- YAN MENÜ ---
with st.sidebar:
    st.header("Analiz Ayarları")
    lig_secimi = st.selectbox("Lig Seç:", ("Türkiye Süper Lig", "İngiltere Premier Lig"))
    st.info("⚠️ Kahin analizi için maçlar oynandıktan sonra veriler güncellenir. Canlı skorlar yukarıdadır.")

if lig_secimi == "Türkiye Süper Lig": df = veri_getir("TR")
else: df = veri_getir("EN")

if df is not None:
    takimlar = sorted(df['HomeTeam'].unique())
    col1, col2 = st.columns(2)
    with col1: ev = st.selectbox("Ev Sahibi", takimlar)
    with col2: dep = st.selectbox("Deplasman", takimlar, index=1)

    if st.button("🔮 KAHİNE SOR", type="primary", use_container_width=True):
        ev_stats = df[df['HomeTeam'] == ev]
        dep_stats = df[df['AwayTeam'] == dep]
        
        if len(ev_stats) > 0 and len(dep_stats) > 0:
            ev_guc = (ev_stats['FTHG'].mean() + ev_stats['HST'].mean()/2) / 2
            dep_guc = (dep_stats['FTAG'].mean() + dep_stats['AST'].mean()/2) / 2
            
            fark = ev_guc - dep_guc
            
            col_a, col_b = st.columns(2)
            col_a.metric("Ev Gücü", f"{ev_guc:.2f}")
            col_b.metric("Dep Gücü", f"{dep_guc:.2f}")
            
            if fark > 0.3: st.success(f"🏆 {ev} Galibiyete Yakın!")
            elif fark < -0.3: st.error(f"🏆 {dep} Galibiyete Yakın!")
            else: st.warning("⚖️ Beraberlik Riski Yüksek!")
        else:
            st.warning("Yeterli veri yok.")
