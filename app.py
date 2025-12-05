import streamlit as st
import streamlit.components.v1 as components 
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from scipy.stats import poisson

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Futbol Kahini 2025-26", page_icon="🦁", layout="wide")

# --- CSS ---
st.markdown("""
<style>
    .stApp { background-color: #050505; color: #E0E0E0; }
    h1, h2, h3, h4 { color: #00E676 !important; font-family: 'Arial Black', sans-serif; text-transform: uppercase; }
    .metric-card { background: linear-gradient(145deg, #1a1a1a, #121212); padding: 15px; border-radius: 12px; border-left: 5px solid #00E676; text-align: center; margin-bottom: 10px; }
    .metric-value { font-size: 24px; font-weight: bold; color: white; margin-top: 5px; }
    .metric-label { font-size: 12px; color: #aaa; letter-spacing: 1px; }
    .analysis-box { background-color: #1E1E1E; padding: 20px; border-radius: 10px; border: 1px solid #333; margin-top: 15px; }
    .stButton>button { background-color: #00E676; color: black !important; font-weight: 900 !important; border-radius: 8px; height: 50px; width: 100%; font-size: 18px !important; }
    .stTabs [aria-selected="true"] { background-color: #00E676; color: black !important; }
</style>
""", unsafe_allow_html=True)

# --- 2025-2026 SEZONU GÜNCEL TAKIM LİSTELERİ (SABİT) ---
# Burası senin istediğin güncel takımlar. CSV'den bağımsız çalışır.
SEZON_2026_TAKIMLARI = {
    "🇹🇷 Türkiye Süper Lig": [
        "Galatasaray", "Fenerbahçe", "Beşiktaş", "Trabzonspor", "Başakşehir", "Kasımpaşa", 
        "Sivasspor", "Alanyaspor", "Rizespor", "Antalyaspor", "Gaziantep FK", "Adana Demirspor", 
        "Samsunspor", "Kayserispor", "Hatayspor", "Konyaspor", "Eyüpspor", "Göztepe", "Bodrum FK"
    ],
    "🇬🇧 İngiltere Premier": [
        "Man City", "Arsenal", "Liverpool", "Aston Villa", "Tottenham", "Chelsea", "Man Utd", 
        "Newcastle", "West Ham", "Brighton", "Bournemouth", "Fulham", "Wolves", "Everton", 
        "Brentford", "Crystal Palace", "Nottm Forest", "Leicester", "Ipswich", "Southampton"
    ],
    "🇪🇸 İspanya La Liga": [
        "Real Madrid", "Barcelona", "Girona", "Atl. Madrid", "Athletic Bilbao", "Real Sociedad", 
        "Betis", "Villarreal", "Valencia", "Alaves", "Osasuna", "Getafe", "Celta Vigo", "Sevilla", 
        "Mallorca", "Las Palmas", "Rayo Vallecano", "Leganes", "Valladolid", "Espanyol"
    ],
    "🇩🇪 Almanya Bundesliga": [
        "Leverkusen", "Stuttgart", "Bayern Munich", "RB Leipzig", "Dortmund", "Frankfurt", 
        "Hoffenheim", "Heidenheim", "Werder Bremen", "Freiburg", "Augsburg", "Wolfsburg", 
        "Mainz", "Gladbach", "Union Berlin", "Bochum", "St. Pauli", "Holstein Kiel"
    ],
    "🇮🇹 İtalya Serie A": [
        "Inter", "Milan", "Juventus", "Bologna", "Atalanta", "Roma", "Lazio", "Fiorentina", 
        "Torino", "Napoli", "Genoa", "Monza", "Verona", "Lecce", "Udinese", "Cagliari", 
        "Empoli", "Parma", "Como", "Venezia"
    ],
    "🇫🇷 Fransa Ligue 1": [
        "PSG", "Monaco", "Brest", "Lille", "Nice", "Lyon", "Lens", "Marseille", "Reims", 
        "Rennes", "Toulouse", "Montpellier", "Strasbourg", "Nantes", "Le Havre", "Auxerre", 
        "Angers", "St Etienne"
    ]
}

# --- VERİ URL'LERİ ---
CSV_LINKS = {
    "🇹🇷 Türkiye Süper Lig": "T1.csv", "🇬🇧 İngiltere Premier": "E0.csv", 
    "🇪🇸 İspanya La Liga": "SP1.csv", "🇩🇪 Almanya Bundesliga": "D1.csv", 
    "🇮🇹 İtalya Serie A": "I1.csv", "🇫🇷 Fransa Ligue 1": "F1.csv"
}

TAKIM_MAP = {
    "Fenerbahce": "Fenerbahçe", "Galatasaray": "Galatasaray", "Besiktas": "Beşiktaş", 
    "Basaksehir": "Başakşehir", "Goztepe": "Göztepe", "Eyupspor": "Eyüpspor", "Bodrumspor": "Bodrum FK",
    "Man City": "Man City", "Man United": "Man Utd", "Leicester": "Leicester"
}

# --- VERİ ÇEKME VE PROFİL OLUŞTURMA ---
@st.cache_data(ttl=3600)
def veri_getir(lig_adi):
    url = f"https://www.football-data.co.uk/mmz4281/2425/{CSV_LINKS.get(lig_adi, 'E0.csv')}"
    try:
        df = pd.read_csv(url)
        df = df.dropna(subset=['HomeTeam', 'AwayTeam', 'FTHG'])
        df['HomeTeam'] = df['HomeTeam'].replace(TAKIM_MAP)
        df['AwayTeam'] = df['AwayTeam'].replace(TAKIM_MAP)
        return df
    except:
        return None

# --- GELİŞMİŞ HİBRİT ANALİZ MOTORU ---
def analiz_motoru(ev, dep, df):
    # 1. GERÇEK VERİ VAR MI?
    ev_stats = df[df['HomeTeam'] == ev] if df is not None else pd.DataFrame()
    dep_stats = df[df['AwayTeam'] == dep] if df is not None else pd.DataFrame()
    
    # 2. PROFİL OLUŞTURMA (Veri yoksa Simülasyon Profili ata)
    def get_profile(stats, team_name, is_home):
        if not stats.empty:
            # Gerçek Veri
            gol_at = stats['FTHG'].mean() if is_home else stats['FTAG'].mean()
            gol_ye = stats['FTAG'].mean() if is_home else stats['FTHG'].mean()
            sut = stats['HS'].mean() if is_home and 'HS' in stats else (stats['AS'].mean() if 'AS' in stats else 11.5)
            return gol_at, gol_ye, sut, "Gerçek Veri"
        else:
            # SİMÜLASYON VERİSİ (Takım büyüklüğüne göre tahmin)
            if team_name in ["Fenerbahçe", "Galatasaray", "Man City", "Real Madrid", "Bayern Munich", "PSG", "Inter"]:
                return (2.4, 0.8, 16.5, "Simülasyon (Favori)") # Güçlü Takım Profili
            elif team_name in ["Eyüpspor", "Bodrum FK", "Göztepe", "Ipswich", "St. Pauli", "Como"]:
                return (1.1, 1.4, 9.5, "Simülasyon (Yeni Çıkan)") # Yeni Takım Profili
            else:
                return (1.3, 1.3, 11.0, "Simülasyon (Orta Sıra)") # Standart Takım

    ev_g, ev_y, ev_sut, ev_tip = get_profile(ev_stats, ev, True)
    dep_g, dep_y, dep_sut, dep_tip = get_profile(dep_stats, dep, False)

    # 3. POISSON HESAPLAMA
    ev_xg = (ev_g + dep_y) / 2 * 1.15 # Ev sahibi avantajı
    dep_xg = (dep_g + ev_y) / 2
    
    ev_dist = [poisson.pmf(i, ev_xg) for i in range(6)]
    dep_dist = [poisson.pmf(i, dep_xg) for i in range(6)]
    matrix = np.outer(ev_dist, dep_dist)
    
    ms1 = np.tril(matrix, -1).sum() * 100
    ms0 = np.trace(matrix) * 100
    ms2 = np.triu(matrix, 1).sum() * 100
    
    kg_var = (1 - (matrix[0,:].sum() + matrix[:,0].sum() - matrix[0,0])) * 100
    ust = (1 - (matrix[0,0] + matrix[1,0] + matrix[0,1] + matrix[1,1] + matrix[2,0] + matrix[0,2])) * 100
    
    skor = f"{int(round(ev_xg))} - {int(round(dep_xg))}"
    
    return {
        "skor": skor, "ms1": ms1, "ms0": ms0, "ms2": ms2,
        "kg": kg, "ust": ust,
        "ev_xg": ev_xg, "dep_xg": dep_xg,
        "ev_sut": ev_sut, "dep_sut": dep_sut,
        "veri_kaynagi": f"Ev: {ev_tip} | Dep: {dep_tip}"
    }

# --- ARAYÜZ ---
st.title("🦁 FUTBOL KAHİNİ V39 (2025-2026 SEZONU)")

tab1, tab2, tab3 = st.tabs(["📊 PRO ANALİZ", "📝 RAW VERİ", "🤖 ASİSTAN"])

# ================= SEKME 1: ANALİZ =================
with tab1:
    st.markdown("### 🕵️‍♂️ 2025-2026 GÜNCEL KADRO ANALİZİ")
    
    c1, c2, c3 = st.columns([2,2,2])
    with c1: lig = st.selectbox("LİG SEÇİNİZ", list(SEZON_2026_TAKIMLARI.keys()))
    
    # ARTIK LİSTELER SABİT VE DOĞRU
    takimlar = sorted(SEZON_2026_TAKIMLARI[lig])
    df = veri_getir(lig)
    
    with c2: ev = st.selectbox("EV SAHİBİ", takimlar)
    with c3: dep = st.selectbox("DEPLASMAN", takimlar, index=1)
    
    if st.button("DETAYLI ANALİZİ BAŞLAT 🚀"):
        res = analiz_motoru(ev, dep, df)
        
        st.divider()
        if "Simülasyon" in res['veri_kaynagi']:
            st.info(f"ℹ️ **BİLGİ:** {ev} veya {dep} için resmi maç verisi henüz oluşmadığı için 'Takım Profili Simülasyonu' kullanıldı.")
        
        # 1. KARTLAR
        k1, k2, k3, k4 = st.columns(4)
        with k1: st.markdown(f"""<div class="metric-card"><div class="metric-label">SKOR TAHMİNİ</div><div class="metric-value">{res['skor']}</div></div>""", unsafe_allow_html=True)
        with k2: st.markdown(f"""<div class="metric-card"><div class="metric-label">EV SAHİBİ (MS1)</div><div class="metric-value">% {res['ms1']:.1f}</div></div>""", unsafe_allow_html=True)
        with k3: st.markdown(f"""<div class="metric-card"><div class="metric-label">2.5 ÜST</div><div class="metric-value">% {res['ust']:.1f}</div></div>""", unsafe_allow_html=True)
        with k4: st.markdown(f"""<div class="metric-card"><div class="metric-label">KG VAR</div><div class="metric-value">% {res['kg']:.1f}</div></div>""", unsafe_allow_html=True)
        
        # 2. GRAFİKLER
        g1, g2 = st.columns(2)
        with g1:
            # Pasta Grafik
            fig_pie = go.Figure(data=[go.Pie(labels=[ev, 'Beraberlik', dep], values=[res['ms1'], res['ms0'], res['ms2']], hole=.4, marker_colors=['#00E676', '#757575', '#FF5252'])])
            fig_pie.update_layout(title="Kazanma Olasılıkları", paper_bgcolor='rgba(0,0,0,0)', font={'color':'white'})
            st.plotly_chart(fig_pie, use_container_width=True)
            
        with g2:
             # Bar Chart (xG)
            fig_bar = go.Figure(data=[
                go.Bar(name='Gol Beklentisi', x=[ev, dep], y=[res['ev_xg'], res['dep_xg']], marker_color='#29B6F6'),
                go.Bar(name='Şut Gücü', x=[ev, dep], y=[res['ev_sut'], res['dep_sut']], marker_color='#FFA726')
            ])
            fig_bar.update_layout(title="Hücum Gücü Karşılaştırması", barmode='group', paper_bgcolor='rgba(0,0,0,0)', font={'color':'white'})
            st.plotly_chart(fig_bar, use_container_width=True)
            
        # 3. DETAYLI YORUM
        st.markdown(f"""
        <div class="analysis-box">
            <h4 style="color:#00E676;">🎙️ YAPAY ZEKA RAPORU</h4>
            <p><b>{ev}</b> takımının gol beklentisi (xG): <b>{res['ev_xg']:.2f}</b><br>
            <b>{dep}</b> takımının gol beklentisi (xG): <b>{res['dep_xg']:.2f}</b></p>
            <p>Bu verilere göre maçın <b>{res['skor']}</b> skoruna yakın bitmesi bekleniyor. 
            Veri kaynağı analizi: <i>{res['veri_kaynagi']}</i>.</p>
        </div>
        """, unsafe_allow_html=True)

# ================= SEKME 2: RAW VERİ =================
with tab2:
    st.markdown("### 📝 HAM VERİ MERKEZİ")
    if df is not None:
        st.dataframe(df.tail(20), use_container_width=True)
    else:
        st.warning("Veri kaynağına bağlanılamadı.")

# ================= SEKME 3: ASİSTAN =================
with tab3:
    st.markdown("### 🤖 ASİSTAN JARVIS")
    if "messages" not in st.session_state: st.session_state.messages = [{"role": "assistant", "content": "2025-2026 sezonu için hazırım!"}]
    for msg in st.session_state.messages: st.chat_message(msg["role"]).write(msg["content"])
    if prompt := st.chat_input("Yaz bakalım..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        st.chat_message("assistant").write("Analiz sonuçlarına göre yorumluyorum...")
