import streamlit as st
import streamlit.components.v1 as components 
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from scipy.stats import poisson

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Futbol Kahini 2025", page_icon="🦁", layout="wide")

# --- CSS (NEON & MODERN) ---
st.markdown("""
<style>
    .stApp { background-color: #050505; color: #E0E0E0; }
    h1, h2, h3, h4 { color: #00E676 !important; font-family: 'Arial Black', sans-serif; text-transform: uppercase; }
    
    /* KARTLAR */
    .metric-card {
        background: linear-gradient(145deg, #1a1a1a, #121212);
        padding: 15px; border-radius: 12px; border-left: 5px solid #00E676;
        text-align: center; margin-bottom: 10px; box-shadow: 0 4px 15px rgba(0,230,118,0.1);
    }
    .metric-value { font-size: 24px; font-weight: bold; color: white; margin-top: 5px; }
    .metric-label { font-size: 12px; color: #aaa; letter-spacing: 1px; }

    /* ANALİZ KUTUSU */
    .analysis-box {
        background-color: #1E1E1E; padding: 20px; border-radius: 10px; border: 1px solid #333; margin-top: 15px;
    }
    
    /* SEÇİM KUTULARI */
    .stSelectbox label p { font-size: 16px !important; color: #00E676 !important; font-weight: bold; }
    div[data-baseweb="select"] > div { background-color: #121212 !important; border: 1px solid #00E676 !important; color: white !important; }

    /* Buton */
    .stButton>button { 
        background-color: #00E676; color: black !important; font-weight: 900 !important; border-radius: 8px; height: 50px; width: 100%; font-size: 18px !important;
    }
    .stTabs [aria-selected="true"] { background-color: #00E676; color: black !important; }
</style>
""", unsafe_allow_html=True)

# --- 2024-2025 SEZONU RESMİ VE GÜNCEL TAKIM LİSTELERİ ---
# Bu liste sabittir. Veri kaynağı hata yapsa bile burası doğru kalır.
LIG_TAKIMLARI = {
    "🇹🇷 Süper Lig": [
        "Galatasaray", "Fenerbahçe", "Beşiktaş", "Trabzonspor", "Başakşehir", "Kasımpaşa", 
        "Sivasspor", "Alanyaspor", "Rizespor", "Antalyaspor", "Gaziantep FK", "Adana Demirspor", 
        "Samsunspor", "Kayserispor", "Hatayspor", "Konyaspor", "Eyüpspor", "Göztepe", "Bodrum FK"
    ],
    "🇬🇧 Premier Lig": [
        "Man City", "Arsenal", "Liverpool", "Aston Villa", "Tottenham", "Chelsea", "Newcastle", 
        "Man Utd", "West Ham", "Crystal Palace", "Brighton", "Bournemouth", "Fulham", "Wolves", 
        "Everton", "Brentford", "Nottingham", "Leicester", "Ipswich", "Southampton"
    ],
    "🇪🇸 La Liga": [
        "Real Madrid", "Barcelona", "Girona", "Atl. Madrid", "Athletic Bilbao", "Real Sociedad", 
        "Betis", "Villarreal", "Valencia", "Alaves", "Osasuna", "Getafe", "Celta Vigo", "Sevilla", 
        "Mallorca", "Las Palmas", "Rayo Vallecano", "Leganes", "Valladolid", "Espanyol"
    ],
    "🇩🇪 Bundesliga": [
        "Leverkusen", "Stuttgart", "Bayern Munich", "RB Leipzig", "Dortmund", "Frankfurt", 
        "Hoffenheim", "Heidenheim", "Werder Bremen", "Freiburg", "Augsburg", "Wolfsburg", 
        "Mainz", "Gladbach", "Union Berlin", "Bochum", "St. Pauli", "Holstein Kiel"
    ],
    "🇮🇹 Serie A": [
        "Inter", "Milan", "Juventus", "Bologna", "Atalanta", "Roma", "Lazio", "Fiorentina", 
        "Torino", "Napoli", "Genoa", "Monza", "Verona", "Lecce", "Udinese", "Cagliari", 
        "Empoli", "Parma", "Como", "Venezia"
    ],
    "🇫🇷 Ligue 1": [
        "PSG", "Monaco", "Brest", "Lille", "Nice", "Lyon", "Lens", "Marseille", "Reims", 
        "Rennes", "Toulouse", "Montpellier", "Strasbourg", "Nantes", "Le Havre", "Auxerre", 
        "Angers", "St Etienne"
    ]
}

# --- VERİ İNDİRME LİNKLERİ (LİGLER) ---
CSV_LINKS = {
    "🇹🇷 Süper Lig": "T1.csv",
    "🇬🇧 Premier Lig": "E0.csv",
    "🇪🇸 La Liga": "SP1.csv",
    "🇩🇪 Bundesliga": "D1.csv",
    "🇮🇹 Serie A": "I1.csv",
    "🇫🇷 Ligue 1": "F1.csv"
}

# İsim Eşleştirme (CSV'deki isimleri Bizim Listeye Çevirir)
ISIM_DUZELTME = {
    "Fenerbahce": "Fenerbahçe", "Galatasaray": "Galatasaray", "Besiktas": "Beşiktaş",
    "Adana Demir": "Adana Demirspor", "Konyaspor": "Konyaspor", "Kasimpasa": "Kasımpaşa",
    "Gaziantep": "Gaziantep FK", "Kayserispor": "Kayserispor", "Antalyaspor": "Antalyaspor",
    "Alanyaspor": "Alanyaspor", "Sivasspor": "Sivasspor", "Basaksehir": "Başakşehir",
    "Rizespor": "Rizespor", "Samsunspor": "Samsunspor", "Hatayspor": "Hatayspor",
    "Eyupspor": "Eyüpspor", "Goztepe": "Göztepe", "Bodrumspor": "Bodrum FK",
    "Man City": "Man City", "Man United": "Man Utd", "Leicester": "Leicester"
}

# --- GÜVENLİ VERİ FONKSİYONLARI ---
def safe_mean(series):
    return series.mean() if not series.empty else 0.0

@st.cache_data(ttl=3600)
def veri_getir(lig_adi):
    base_url = "https://www.football-data.co.uk/mmz4281/2425/" # 24/25 Sezonu
    csv_code = CSV_LINKS.get(lig_adi)
    
    if not csv_code: return None
    
    try:
        url = base_url + csv_code
        df = pd.read_csv(url)
        df = df.dropna(subset=['HomeTeam', 'AwayTeam', 'FTHG'])
        
        # İsimleri Türkçeleştir
        df['HomeTeam'] = df['HomeTeam'].replace(ISIM_DUZELTME)
        df['AwayTeam'] = df['AwayTeam'].replace(ISIM_DUZELTME)
        return df
    except:
        return None

# --- POISSON & ANALİZ MOTORU ---
def poisson_hesapla(ev_val, dep_val):
    ev_dist = [poisson.pmf(i, ev_val) for i in range(6)]
    dep_dist = [poisson.pmf(i, dep_val) for i in range(6)]
    matrix = np.outer(ev_dist, dep_dist)
    
    ms1 = np.tril(matrix, -1).sum() * 100
    ms0 = np.trace(matrix) * 100
    ms2 = np.triu(matrix, 1).sum() * 100
    
    kg_var = (1 - (matrix[0,:].sum() + matrix[:,0].sum() - matrix[0,0])) * 100
    ust = (1 - (matrix[0,0] + matrix[1,0] + matrix[0,1] + matrix[1,1] + matrix[2,0] + matrix[0,2])) * 100
    
    return ms1, ms0, ms2, kg_var, ust

def detayli_analiz(ev, dep, df):
    # Veri varsa çek, yoksa varsayılan (Yeni takım simülasyonu)
    if df is not None:
        ev_stats = df[df['HomeTeam'] == ev]
        dep_stats = df[df['AwayTeam'] == dep]
        lig_gol_ort = df['FTHG'].mean() + df['FTAG'].mean()
    else:
        ev_stats = pd.DataFrame()
        dep_stats = pd.DataFrame()
        lig_gol_ort = 2.5 # Varsayılan lig ortalaması

    # Veri yoksa (Yeni Sezon/Yeni Takım) -> Ortalama değerler ata
    ev_g = safe_mean(ev_stats['FTHG']) if not ev_stats.empty else 1.3
    ev_y = safe_mean(ev_stats['FTAG']) if not ev_stats.empty else 1.1
    dep_g = safe_mean(dep_stats['FTAG']) if not dep_stats.empty else 1.0
    dep_y = safe_mean(dep_stats['FTHG']) if not dep_stats.empty else 1.4
    
    ev_sut = safe_mean(ev_stats['HS']) if not ev_stats.empty and 'HS' in ev_stats else 12.5
    dep_sut = safe_mean(dep_stats['AS']) if not dep_stats.empty and 'AS' in dep_stats else 10.0
    
    # Poisson Beklentileri
    ev_beklenti = (ev_g + dep_y) / 2 * 1.1 (ev sahibi avantajı)
    dep_beklenti = (dep_g + ev_y) / 2
    
    ms1, ms0, ms2, kg, ust = poisson_hesapla(ev_beklenti, dep_beklenti)
    
    # Skor Tahmini
    skor_ev = int(round(ev_beklenti))
    skor_dep = int(round(dep_beklenti))
    
    # İbre
    ibre = ms1 + (ms0 / 3) # Basit güç skoru
    
    return {
        "skor": f"{skor_ev} - {skor_dep}",
        "ms1": ms1, "ms0": ms0, "ms2": ms2,
        "kg": kg, "ust": ust,
        "ev_xg": ev_beklenti, "dep_xg": dep_beklenti,
        "ev_sut": ev_sut, "dep_sut": dep_sut,
        "veri_durumu": "Gerçek Veri" if not ev_stats.empty else "Simülasyon (Yetersiz Veri)"
    }

# --- ARAYÜZ ---
st.title("🦁 FUTBOL KAHİNİ V36")

tab1, tab2, tab3 = st.tabs(["📊 PRO ANALİZ", "📝 RAW VERİ", "🤖 ASİSTAN"])

# ================= SEKME 1: ANALİZ =================
with tab1:
    st.markdown("### 🕵️‍♂️ BİLİMSEL MAÇ ANALİZİ")
    
    c1, c2, c3 = st.columns([2,2,2])
    with c1: lig = st.selectbox("LİG SEÇİNİZ", list(LIG_TAKIMLARI.keys()))
    
    # Data Yükle
    df = veri_getir(lig)
    
    # Takımları Sabit Listeden Çek (Data'da olmasa bile listede görünür!)
    takimlar = sorted(LIG_TAKIMLARI[lig])
    
    with c2: ev = st.selectbox("EV SAHİBİ", takimlar)
    with c3: dep = st.selectbox("DEPLASMAN", takimlar, index=1)
    
    if st.button("DETAYLI ANALİZİ BAŞLAT 🚀"):
        res = detayli_analiz(ev, dep, df)
        
        # --- UYARI EĞER VERİ YOKSA ---
        if res['veri_durumu'] != "Gerçek Veri":
            st.warning(f"⚠️ **DİKKAT:** {ev} veya {dep} için bu sezon henüz yeterli maç verisi oluşmamış. Analiz, lig ortalamaları ve simülasyon üzerinden yapılmıştır.")
        
        st.divider()
        
        # --- KARTLAR ---
        k1, k2, k3, k4 = st.columns(4)
        with k1: st.markdown(f"""<div class="metric-card"><div class="metric-label">SKOR TAHMİNİ</div><div class="metric-value">{res['skor']}</div></div>""", unsafe_allow_html=True)
        with k2: st.markdown(f"""<div class="metric-card"><div class="metric-label">EV SAHİBİ KAZANIR</div><div class="metric-value">% {res['ms1']:.1f}</div></div>""", unsafe_allow_html=True)
        with k3: st.markdown(f"""<div class="metric-card"><div class="metric-label">2.5 ÜST İHTİMALİ</div><div class="metric-value">% {res['ust']:.1f}</div></div>""", unsafe_allow_html=True)
        with k4: st.markdown(f"""<div class="metric-card"><div class="metric-label">KG VAR İHTİMALİ</div><div class="metric-value">% {res['kg']:.1f}</div></div>""", unsafe_allow_html=True)
        
        # --- GRAFİKLER ---
        g1, g2 = st.columns(2)
        with g1:
            fig_pie = go.Figure(data=[go.Pie(labels=[f'{ev}', 'Beraberlik', f'{dep}'], values=[res['ms1'], res['ms0'], res['ms2']], hole=.4, marker_colors=['#00E676', '#757575', '#FF5252'])])
            fig_pie.update_layout(title="Kazanma Olasılıkları", paper_bgcolor='rgba(0,0,0,0)', font={'color':'white'})
            st.plotly_chart(fig_pie, use_container_width=True)
            
        with g2:
            fig_bar = go.Figure(data=[
                go.Bar(name='Gol Beklentisi (xG)', x=[ev, dep], y=[res['ev_xg'], res['dep_xg']], marker_color='#29B6F6'),
                go.Bar(name='Şut Ortalaması', x=[ev, dep], y=[res['ev_sut'], res['dep_sut']], marker_color='#FFA726')
            ])
            fig_bar.update_layout(title="Hücum Gücü Karşılaştırması", paper_bgcolor='rgba(0,0,0,0)', font={'color':'white'}, barmode='group')
            st.plotly_chart(fig_bar, use_container_width=True)
            
        # --- YORUM ---
        st.markdown(f"""
        <div class="analysis-box">
            <h4 style="color:#00E676;">🎙️ YAPAY ZEKA YORUMU</h4>
            <p>Matematiksel Poisson dağılımına göre, ev sahibi <b>{ev}</b> maçta favori görünüyor (%{res['ms1']:.1f}). 
            İki takımın gol beklentisi (xG) toplamı <b>{res['ev_xg'] + res['dep_xg']:.2f}</b> seviyesinde. 
            Bu da maçın {('hareketli ve gollü' if res['ev_xg'] + res['dep_xg'] > 2.5 else 'kontrollü ve düşük skorlu')} geçebileceğini işaret ediyor.</p>
            <p>Risk almak isteyenler için <b>KG VAR (%{res['kg']:.1f})</b> seçeneği değerlendirilebilir.</p>
        </div>
        """, unsafe_allow_html=True)

# ================= SEKME 2: RAW VERİ =================
with tab2:
    st.markdown("### 📝 HAM VERİ MERKEZİ")
    if df is not None:
        st.dataframe(df.tail(20), use_container_width=True)
        st.caption("Veriler: football-data.co.uk (Son 20 Maç)")
    else:
        st.info("Bu lig için henüz ham veri CSV dosyasına işlenmemiş. Ancak yukarıdaki analiz simülasyon modunda çalışmaktadır.")

# ================= SEKME 3: ASİSTAN =================
with tab3:
    st.markdown("### 🤖 ASİSTAN JARVIS")
    if "messages" not in st.session_state: st.session_state.messages = [{"role": "assistant", "content": "Merhaba! Hangi takımı analiz etmemi istersin?"}]
    for msg in st.session_state.messages: st.chat_message(msg["role"]).write(msg["content"])
    if prompt := st.chat_input("Yaz bakalım..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        st.chat_message("assistant").write("Analiz sekmesindeki verileri inceleyip sana döneceğim.")
