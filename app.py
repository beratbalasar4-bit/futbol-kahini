import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson
import plotly.graph_objects as go
import plotly.express as px

# --- 1. YAPILANDIRMA VE CSS ---
st.set_page_config(page_title="Futbol Kahini AI", page_icon="🧠", layout="wide")

st.markdown("""
<style>
    /* Modern Dark Tema */
    .stApp { background-color: #0E1117; color: #FAFAFA; }
    
    /* Başlıklar */
    h1, h2, h3 { font-family: 'Helvetica Neue', sans-serif; font-weight: 800; color: #00E5FF; }
    
    /* Kart Tasarımları */
    .kpi-card {
        background: linear-gradient(135deg, #1e293b, #0f172a);
        padding: 20px; border-radius: 15px; border: 1px solid #334155;
        text-align: center; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 10px;
    }
    .kpi-title { font-size: 14px; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; }
    .kpi-value { font-size: 32px; font-weight: bold; color: #38bdf8; margin-top: 10px; }
    
    /* Tahmin Kutusu */
    .prediction-box {
        background-color: #111827; border-left: 5px solid #00E5FF; padding: 20px; border-radius: 8px;
    }
    
    /* Tablo Düzeni */
    div[data-testid="stDataFrame"] { border: 1px solid #334155; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# --- 2. VERİTABANI (INTERNAL DB - GÜÇ PUANLARI) ---
# Burası bizim sigortamız. Veri çekilemezse veya yeni takımsa buradaki puanlar devreye girer.
# Puanlar 100 üzerinden güncel güç dengesidir (2025-2026 Tahmini).

TAKIM_VERITABANI = {
    "🇹🇷 Süper Lig": {
        "Galatasaray": 88, "Fenerbahçe": 87, "Beşiktaş": 82, "Trabzonspor": 78,
        "Başakşehir": 75, "Kasımpaşa": 70, "Sivasspor": 68, "Alanyaspor": 67,
        "Rizespor": 66, "Antalyaspor": 66, "Samsunspor": 72, "Göztepe": 68,
        "Eyüpspor": 70, "Bodrum FK": 64, "Konyaspor": 65, "Kayserispor": 65,
        "Gaziantep FK": 63, "Hatayspor": 62, "Adana Demirspor": 60 
    },
    "🇬🇧 Premier Lig": {
        "Man City": 96, "Arsenal": 94, "Liverpool": 93, "Aston Villa": 85,
        "Tottenham": 84, "Chelsea": 83, "Newcastle": 82, "Man Utd": 81,
        "West Ham": 78, "Brighton": 79, "Fulham": 75, "Bournemouth": 74,
        "Crystal Palace": 73, "Wolves": 72, "Everton": 71, "Brentford": 70,
        "Nottm Forest": 70, "Leicester": 68, "Ipswich": 66, "Southampton": 67
    },
    "🇪🇸 La Liga": {
        "Real Madrid": 95, "Barcelona": 92, "Atl. Madrid": 88, "Girona": 84,
        "Athletic Bilbao": 82, "Real Sociedad": 80, "Betis": 79, "Villarreal": 78,
        "Valencia": 75, "Sevilla": 74, "Celta Vigo": 72, "Osasuna": 71,
        "Mallorca": 70, "Las Palmas": 68, "Alaves": 68, "Rayo Vallecano": 67,
        "Getafe": 66, "Leganes": 65, "Valladolid": 64, "Espanyol": 65
    },
    "🇩🇪 Bundesliga": {
        "Leverkusen": 92, "Bayern Munich": 91, "Dortmund": 87, "RB Leipzig": 86,
        "Stuttgart": 84, "Frankfurt": 80, "Hoffenheim": 76, "Freiburg": 75,
        "Werder Bremen": 72, "Augsburg": 70, "Wolfsburg": 71, "Heidenheim": 69,
        "Mainz": 68, "Gladbach": 70, "Union Berlin": 68, "Bochum": 65,
        "St. Pauli": 64, "Holstein Kiel": 63
    },
    "🇮🇹 Serie A": {
        "Inter": 93, "Milan": 88, "Juventus": 87, "Atalanta": 85,
        "Roma": 82, "Lazio": 81, "Napoli": 84, "Bologna": 80,
        "Fiorentina": 78, "Torino": 75, "Genoa": 72, "Monza": 71,
        "Lecce": 68, "Udinese": 69, "Empoli": 67, "Verona": 66,
        "Parma": 65, "Como": 66, "Venezia": 64, "Cagliari": 65
    },
    "🇫🇷 Ligue 1": {
        "PSG": 94, "Monaco": 86, "Lille": 84, "Brest": 80,
        "Nice": 79, "Lyon": 82, "Marseille": 83, "Lens": 78,
        "Rennes": 77, "Reims": 74, "Toulouse": 72, "Montpellier": 70,
        "Strasbourg": 71, "Nantes": 69, "Le Havre": 66, "St Etienne": 68,
        "Auxerre": 65, "Angers": 64
    }
}

# CSV Linkleri (Canlı Veri İçin)
CSV_URLS = {
    "🇹🇷 Süper Lig": "T1", "🇬🇧 Premier Lig": "E0", "🇪🇸 La Liga": "SP1",
    "🇩🇪 Bundesliga": "D1", "🇮🇹 Serie A": "I1", "🇫🇷 Ligue 1": "F1"
}

# --- 3. FONKSİYONLAR ---

@st.cache_data(ttl=1800) # 30 dk cache
def fetch_live_data(league_code):
    """İnternetten canlı veriyi çeker. Hata verirse None döner."""
    try:
        url = f"https://www.football-data.co.uk/mmz4281/2425/{league_code}.csv"
        df = pd.read_csv(url)
        df = df.dropna(subset=['HomeTeam', 'AwayTeam', 'FTHG']) # Temizlik
        return df
    except:
        return None

def normalize_name(name):
    """Takım isimlerini standartlaştırır."""
    mapping = {
        "Fenerbahce": "Fenerbahçe", "Galatasaray": "Galatasaray", "Besiktas": "Beşiktaş",
        "Basaksehir": "Başakşehir", "Goztepe": "Göztepe", "Eyupspor": "Eyüpspor",
        "Bodrumspor": "Bodrum FK", "Man City": "Man City", "Man United": "Man Utd"
    }
    return mapping.get(name, name)

def calculate_metrics(home_team, away_team, df, league_name):
    """
    Hibrit Analiz Motoru:
    1. Önce gerçek veriye (df) bakar.
    2. Veri yoksa veya yetersizse veritabanındaki (TAKIM_VERITABANI) güç puanlarını kullanır.
    """
    
    # Varsayılan (Simülasyon) Değerler
    home_power = TAKIM_VERITABANI[league_name].get(home_team, 70)
    away_power = TAKIM_VERITABANI[league_name].get(away_team, 70)
    
    # Güç farkına göre xG (Gol Beklentisi) Simülasyonu
    power_diff = home_power - away_power
    sim_home_xg = 1.4 + (power_diff * 0.03) + 0.25 # +0.25 Ev sahibi avantajı
    sim_away_xg = 1.1 - (power_diff * 0.03)
    
    # Gerçek Veri Entegrasyonu (Varsa ağırlıklandır)
    data_source = "Simülasyon (Güç Endeksi)"
    
    if df is not None:
        # İsimleri düzeltip filtrele
        df['HomeTeam'] = df['HomeTeam'].apply(normalize_name)
        df['AwayTeam'] = df['AwayTeam'].apply(normalize_name)
        
        home_matches = df[df['HomeTeam'] == home_team]
        away_matches = df[df['AwayTeam'] == away_team]
        
        if len(home_matches) > 2 and len(away_matches) > 2:
            real_home_xg = home_matches['FTHG'].mean()
            real_home_concede = home_matches['FTAG'].mean()
            real_away_xg = away_matches['FTAG'].mean()
            real_away_concede = away_matches['FTHG'].mean()
            
            # Gerçek veri ile simülasyonu harmanla (%70 Gerçek, %30 Simülasyon)
            sim_home_xg = (real_home_xg * 0.7 + sim_home_xg * 0.3)
            sim_away_xg = (real_away_xg * 0.7 + sim_away_xg * 0.3)
            data_source = "Hibrit (Canlı Veri + AI)"
            
    # Negatif değerleri engelle
    sim_home_xg = max(0.1, sim_home_xg)
    sim_away_xg = max(0.1, sim_away_xg)
            
    return sim_home_xg, sim_away_xg, data_source

def run_poisson_simulation(home_xg, away_xg):
    """Poisson dağılımı ile 1000 maç simüle eder gibi olasılık hesaplar."""
    home_dist = [poisson.pmf(i, home_xg) for i in range(6)]
    away_dist = [poisson.pmf(i, away_xg) for i in range(6)]
    matrix = np.outer(home_dist, away_dist)
    
    win_prob = np.tril(matrix, -1).sum() * 100
    draw_prob = np.trace(matrix) * 100
    loss_prob = np.triu(matrix, 1).sum() * 100
    
    over_25_prob = (1 - (matrix[0,0] + matrix[1,0] + matrix[0,1] + matrix[1,1] + matrix[2,0] + matrix[0,2])) * 100
    btts_prob = (1 - (matrix[0,:].sum() + matrix[:,0].sum() - matrix[0,0])) * 100
    
    return win_prob, draw_prob, loss_prob, over_25_prob, btts_prob

# --- 4. ARAYÜZ (UI) ---

st.title("🦁 FUTBOL KAHİNİ AI - NEXTGEN")
st.caption("Profesyonel Hibrit Analiz Motoru | Veri + Algoritma")

# Sidebar (Ayarlar)
with st.sidebar:
    st.header("⚙️ Ayarlar")
    selected_league = st.selectbox("Lig Seçiniz:", list(TAKIM_VERITABANI.keys()))
    
    # Takımları İç Veritabanından Çek (En Güncel Liste Burasıdır)
    teams = sorted(list(TAKIM_VERITABANI[selected_league].keys()))
    
    st.divider()
    home_team = st.selectbox("Ev Sahibi:", teams, index=0)
    away_team = st.selectbox("Deplasman:", teams, index=1)
    
    if st.button("Analizi Başlat", use_container_width=True):
        st.session_state['analyzed'] = True
    else:
        st.session_state['analyzed'] = False

# Ana Ekran
if st.session_state.get('analyzed'):
    # Veri Çekme
    csv_code = CSV_URLS.get(selected_league)
    df_live = fetch_live_data(csv_code)
    
    # Hesaplama
    h_xg, a_xg, source = calculate_metrics(home_team, away_team, df_live, selected_league)
    win, draw, loss, over, btts = run_poisson_simulation(h_xg, a_xg)
    
    # Tahmin Skoru
    pred_home_score = int(round(h_xg))
    pred_away_score = int(round(a_xg))
    
    # --- SONUÇ GÖSTERİMİ ---
    
    # 1. Üst Bilgi
    st.info(f"📡 Veri Kaynağı: **{source}** | Lig: **{selected_league}**")
    
    # 2. Ana Skor Kartı
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown(f"""
        <div style="text-align:center; background:#111827; padding:20px; border-radius:15px; border:2px solid #00E5FF;">
            <h2 style="margin:0; color:white;">{home_team} vs {away_team}</h2>
            <h1 style="font-size:64px; margin:10px 0; color:#00E5FF;">{pred_home_score} - {pred_away_score}</h1>
            <p style="color:#aaa;">Tahmini Skor</p>
        </div>
        """, unsafe_allow_html=True)
        
    st.divider()
    
    # 3. KPI Kartları (Detaylı Olasılıklar)
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"""<div class="kpi-card"><div class="kpi-title">EV SAHİBİ KAZANIR</div><div class="kpi-value">%{win:.1f}</div></div>""", unsafe_allow_html=True)
    with k2:
        st.markdown(f"""<div class="kpi-card"><div class="kpi-title">BERABERLİK</div><div class="kpi-value">%{draw:.1f}</div></div>""", unsafe_allow_html=True)
    with k3:
        st.markdown(f"""<div class="kpi-card"><div class="kpi-title">2.5 ÜST</div><div class="kpi-value">%{over:.1f}</div></div>""", unsafe_allow_html=True)
    with k4:
        st.markdown(f"""<div class="kpi-card"><div class="kpi-title">KG VAR</div><div class="kpi-value">%{btts:.1f}</div></div>""", unsafe_allow_html=True)

    # 4. Grafikler
    st.subheader("📊 Görsel Analiz")
    tab_g1, tab_g2 = st.tabs(["Maçın Hakimi Kim?", "Gol Beklentisi (xG)"])
    
    with tab_g1:
        # Gauge Chart (İbre)
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = win,
            title = {'text': f"{home_team} Kazanma Şansı"},
            gauge = {
                'axis': {'range': [0, 100]},
                'bar': {'color': "#00E5FF"},
                'steps': [
                    {'range': [0, 33], 'color': "#ef4444"},
                    {'range': [33, 66], 'color': "#eab308"},
                    {'range': [66, 100], 'color': "#22c55e"}],
            }
        ))
        fig_gauge.update_layout(paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
        st.plotly_chart(fig_gauge, use_container_width=True)
        
    with tab_g2:
        # Bar Chart
        fig_bar = go.Figure(data=[
            go.Bar(name=home_team, x=['Gol Beklentisi'], y=[h_xg], marker_color='#00E5FF'),
            go.Bar(name=away_team, x=['Gol Beklentisi'], y=[a_xg], marker_color='#F43F5E')
        ])
        fig_bar.update_layout(barmode='group', paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"}, title="Hücum Gücü Kıyaslaması")
        st.plotly_chart(fig_bar, use_container_width=True)

    # 5. Yapay Zeka Yorumu
    st.markdown("### 🎙️ Yapay Zeka Yorumu")
    st.markdown(f"""
    <div class="prediction-box">
        <p><b>Maç Analizi:</b> {selected_league} ligindeki güç dengelerine baktığımızda, <b>{home_team}</b> (Güç: {TAKIM_VERITABANI[selected_league][home_team]}) ile 
        <b>{away_team}</b> (Güç: {TAKIM_VERITABANI[selected_league][away_team]}) karşılaşıyor.</p>
        
        <p><b>Senaryo:</b> {'Ev sahibi takımın saha avantajı ve kadro kalitesiyle baskın oynaması bekleniyor.' if h_xg > a_xg else 'Deplasman ekibinin güçlü kadrosuyla maça ağırlığını koyması muhtemel.'}
        Veri motorumuz bu maçta toplam <b>{h_xg + a_xg:.2f}</b> gol beklentisi (xG) hesapladı. 
        {'Bol gollü ve keyifli bir maç olabilir.' if (h_xg + a_xg) > 2.6 else 'Taktiksel ve kontrollü, düşük skorlu bir mücadele beklenebilir.'}</p>
        
        <p><b>Öne Çıkan Bahis:</b> 
        {'MS 1' if win > 55 else ('MS 2' if loss > 55 else 'Beraberlik veya KG Var')} seçeneği istatistiksel olarak öne çıkıyor.</p>
    </div>
    """, unsafe_allow_html=True)

else:
    # Karşılama Ekranı
    st.markdown("""
    <div style="text-align:center; padding: 50px;">
        <h3>👈 Soldaki menüden lig ve takımları seçerek analizi başlatın.</h3>
        <p style="color:#666;">Bu sistem, canlı veriler ile yapay zeka simülasyonunu birleştirerek en doğru sonucu vermeyi hedefler.</p>
    </div>
    """, unsafe_allow_html=True)
