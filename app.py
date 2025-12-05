import streamlit as st
import streamlit.components.v1 as components 
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from scipy.stats import poisson

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Futbol Kahini Pro Live", page_icon="🦁", layout="wide")

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
    
    /* Buton */
    .stButton>button { 
        background-color: #00E676; color: black !important; font-weight: 900 !important; border-radius: 8px; height: 50px; width: 100%; font-size: 18px !important;
    }
    .stTabs [aria-selected="true"] { background-color: #00E676; color: black !important; }
</style>
""", unsafe_allow_html=True)

# --- VERİ LİNKLERİ (CANLI CSV) ---
# Buradaki kodlar (T1, E0 vb.) Football-Data sitesinin resmi kodlarıdır.
# Sezon kodu '2425' (2024-2025) olarak ayarlandı.
LIG_URLLERI = {
    "🇹🇷 Türkiye Süper Lig": "https://www.football-data.co.uk/mmz4281/2425/T1.csv",
    "🇬🇧 İngiltere Premier": "https://www.football-data.co.uk/mmz4281/2425/E0.csv",
    "🇪🇸 İspanya La Liga": "https://www.football-data.co.uk/mmz4281/2425/SP1.csv",
    "🇩🇪 Almanya Bundesliga": "https://www.football-data.co.uk/mmz4281/2425/D1.csv",
    "🇮🇹 İtalya Serie A": "https://www.football-data.co.uk/mmz4281/2425/I1.csv",
    "🇫🇷 Fransa Ligue 1": "https://www.football-data.co.uk/mmz4281/2425/F1.csv",
    "🇳🇱 Hollanda Eredivisie": "https://www.football-data.co.uk/mmz4281/2425/N1.csv",
    "🇵🇹 Portekiz Liga NOS": "https://www.football-data.co.uk/mmz4281/2425/P1.csv",
    "🇧🇪 Belçika Jupiler": "https://www.football-data.co.uk/mmz4281/2425/B1.csv"
}

# Canlı Skor Linkleri (Teyit İçin)
LIVESCORE_LINKS = {
    "🇹🇷 Türkiye Süper Lig": "https://www.flashscore.mobi/standings/W6BOzpK2/U3MvIVsA/#table/overall",
    "🇬🇧 İngiltere Premier": "https://www.flashscore.mobi/standings/dYlOSQ44/W6DOvJ92/#table/overall",
    "🇪🇸 İspanya La Liga": "https://www.flashscore.mobi/standings/QVmLl54o/dG2SqPPf/#table/overall",
    "🇩🇪 Almanya Bundesliga": "https://www.flashscore.mobi/standings/W6BOzpK2/U3MvIVsA/#table/overall",
    "🇮🇹 İtalya Serie A": "https://www.flashscore.mobi/standings/dYlOSQ44/W6DOvJ92/#table/overall",
    "🇫🇷 Fransa Ligue 1": "https://www.flashscore.mobi/standings/W6BOzpK2/U3MvIVsA/#table/overall",
}

# İsim Düzeltmeleri (Sadece okunabilirlik için)
TAKIM_DUZELTME = {
    "Fenerbahce": "Fenerbahçe", "Galatasaray": "Galatasaray", "Besiktas": "Beşiktaş", 
    "Basaksehir": "Başakşehir", "Konyaspor": "Konyaspor", "Kasimpasa": "Kasımpaşa",
    "Gaziantep": "Gaziantep FK", "Kayserispor": "Kayserispor", "Antalyaspor": "Antalyaspor",
    "Alanyaspor": "Alanyaspor", "Sivasspor": "Sivasspor", "Rizespor": "Rizespor",
    "Samsunspor": "Samsunspor", "Hatayspor": "Hatayspor", "Eyupspor": "Eyüpspor",
    "Goztepe": "Göztepe", "Bodrumspor": "Bodrum FK"
}

# --- VERİ YÜKLEME (CACHE MEKANİZMASI) ---
@st.cache_data(ttl=900) # Her 15 dakikada bir veriyi yenile
def veri_getir(url):
    try:
        df = pd.read_csv(url)
        # Boş satırları temizle
        df = df.dropna(subset=['HomeTeam', 'AwayTeam', 'FTHG'])
        # Tarih formatı
        df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
        # İsimleri düzelt
        df['HomeTeam'] = df['HomeTeam'].replace(TAKIM_DUZELTME)
        df['AwayTeam'] = df['AwayTeam'].replace(TAKIM_DUZELTME)
        return df
    except:
        return None

def get_safe_mean(series):
    return series.mean() if not series.empty else 0.0

# --- DİNAMİK TAKIM LİSTESİ ÇEKME ---
def takimlari_getir(df):
    if df is None: return []
    # Hem ev sahibi hem deplasman sütunundaki tüm takımları alıp tekilleştiriyoruz
    tum_takimlar = pd.concat([df['HomeTeam'], df['AwayTeam']]).unique()
    return sorted(tum_takimlar)

# --- POISSON ANALİZ ---
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

# --- ANALİZ MOTORU ---
def analiz_motoru(ev, dep, df):
    ev_stats = df[df['HomeTeam'] == ev]
    dep_stats = df[df['AwayTeam'] == dep]
    
    # Veri Kontrolü (Dinamik listeden geldiği için veri olma ihtimali yüksek ama yine de kontrol)
    if ev_stats.empty and dep_stats.empty:
        return {"hata": "Bu takımlar için henüz yeterli veri yok."}

    # İstatistikler
    ev_g = get_safe_mean(ev_stats['FTHG']); ev_y = get_safe_mean(ev_stats['FTAG'])
    dep_g = get_safe_mean(dep_stats['FTAG']); dep_y = get_safe_mean(dep_stats['FTHG'])
    
    ev_sut = get_safe_mean(ev_stats['HS']) if 'HS' in df.columns else 11.0
    dep_sut = get_safe_mean(dep_stats['AS']) if 'AS' in df.columns else 9.5
    ev_isabet = get_safe_mean(ev_stats['HST']) if 'HST' in df.columns else 4.0
    dep_isabet = get_safe_mean(dep_stats['AST']) if 'AST' in df.columns else 3.5

    # Poisson Beklentisi
    lig_gol_ort = (df['FTHG'].mean() + df['FTAG'].mean()) / 2
    ev_atak = ev_g / lig_gol_ort if lig_gol_ort > 0 else 1.0
    dep_defans = dep_y / lig_gol_ort if lig_gol_ort > 0 else 1.0
    
    ev_xg = ev_atak * dep_defans * lig_gol_ort * 1.15 # Ev sahibi avantajı
    dep_xg = (dep_g / lig_gol_ort) * (ev_y / lig_gol_ort) * lig_gol_ort
    
    ms1, ms0, ms2, kg, ust = poisson_hesapla(ev_xg, dep_xg)
    
    # Skor
    skor = f"{int(round(ev_xg))} - {int(round(dep_xg))}"
    
    # Form Trendi (Son 5 Maç Golleri)
    def get_trend(team_name):
        matches = df[(df['HomeTeam'] == team_name) | (df['AwayTeam'] == team_name)].tail(5)
        trend = []
        for _, row in matches.iterrows():
            if row['HomeTeam'] == team_name: trend.append(row['FTHG'])
            else: trend.append(row['FTAG'])
        return trend

    return {
        "skor": skor, "ms1": ms1, "ms0": ms0, "ms2": ms2,
        "kg": kg, "ust": ust,
        "ev_xg": ev_xg, "dep_xg": dep_xg,
        "ev_sut": ev_sut, "dep_sut": dep_sut,
        "ev_isabet": ev_isabet, "dep_isabet": dep_isabet,
        "ev_trend": get_trend(ev), "dep_trend": get_trend(dep)
    }

# --- ARAYÜZ ---
st.title("🦁 FUTBOL KAHİNİ V38: OTOPİLOT")

tab1, tab2, tab3 = st.tabs(["📊 DETAYLI ANALİZ", "📝 RAW VERİ", "🤖 ASİSTAN"])

# ================= SEKME 1: ANALİZ =================
with tab1:
    st.markdown("### 🕵️‍♂️ CANLI VERİ ANALİZİ")
    st.info("Bu sistem, internetteki en güncel veriyi anlık çeker. Eğer takım ligden düştüyse listede çıkmaz.")
    
    c1, c2, c3 = st.columns([2,2,2])
    with c1: 
        secilen_lig = st.selectbox("LİG SEÇİNİZ", list(LIG_URLLERI.keys()))
        url = LIG_URLLERI[secilen_lig]
    
    # Veriyi Çek
    df = veri_getir(url)
    
    if df is not None:
        # LİSTEYİ DİNAMİK OLUŞTURUYORUZ (EN ÖNEMLİ KISIM)
        takimlar = takimlari_getir(df)
        
        if len(takimlar) > 0:
            with c2: ev = st.selectbox("EV SAHİBİ", takimlar)
            with c3: dep = st.selectbox("DEPLASMAN", takimlar, index=1)
            
            # --- CANLI TEYİT PENCERESİ ---
            with st.expander("📡 Puan Durumu ve Fikstür Teyidi (Flashscore)", expanded=False):
                live_url = LIVESCORE_LINKS.get(secilen_lig, "https://www.flashscore.mobi")
                components.html(f"""<iframe src="{live_url}" width="100%" height="400" frameborder="0"></iframe>""", height=400)

            if st.button("ANALİZ ET 🚀"):
                res = analiz_motoru(ev, dep, df)
                
                if "hata" not in res:
                    st.divider()
                    
                    # 1. KARTLAR
                    k1, k2, k3, k4 = st.columns(4)
                    with k1: st.markdown(f"""<div class="metric-card"><div class="metric-label">SKOR TAHMİNİ</div><div class="metric-value">{res['skor']}</div></div>""", unsafe_allow_html=True)
                    with k2: st.markdown(f"""<div class="metric-card"><div class="metric-label">EV SAHİBİ (MS1)</div><div class="metric-value">% {res['ms1']:.1f}</div></div>""", unsafe_allow_html=True)
                    with k3: st.markdown(f"""<div class="metric-card"><div class="metric-label">2.5 ÜST</div><div class="metric-value">% {res['ust']:.1f}</div></div>""", unsafe_allow_html=True)
                    with k4: st.markdown(f"""<div class="metric-card"><div class="metric-label">KG VAR</div><div class="metric-value">% {res['kg']:.1f}</div></div>""", unsafe_allow_html=True)
                    
                    # 2. GRAFİKLER
                    st.markdown("#### 📈 GRAFİKSEL ANALİZ")
                    g1, g2 = st.columns(2)
                    
                    with g1:
                        # Pasta Grafik
                        fig_pie = go.Figure(data=[go.Pie(labels=[ev, 'Beraberlik', dep], values=[res['ms1'], res['ms0'], res['ms2']], hole=.4, marker_colors=['#00E676', '#757575', '#FF5252'])])
                        fig_pie.update_layout(title="Kazanma Olasılığı", paper_bgcolor='rgba(0,0,0,0)', font={'color':'white'})
                        st.plotly_chart(fig_pie, use_container_width=True)
                        st.caption("Matematiksel Poisson dağılımına göre kazanma şansları.")

                    with g2:
                        # Form Trendi (Çizgi Grafik - Yeni!)
                        fig_trend = go.Figure()
                        fig_trend.add_trace(go.Scatter(y=res['ev_trend'], mode='lines+markers', name=ev, line=dict(color='#00E676', width=3)))
                        fig_trend.add_trace(go.Scatter(y=res['dep_trend'], mode='lines+markers', name=dep, line=dict(color='#FF5252', width=3)))
                        fig_trend.update_layout(title="Son 5 Maç Gol Trendi", paper_bgcolor='rgba(0,0,0,0)', font={'color':'white'}, xaxis_title="Son Maçlar", yaxis_title="Atılan Gol")
                        st.plotly_chart(fig_trend, use_container_width=True)
                        st.caption("Takımların son maçlarında attıkları gol sayıları. Trend yukarıdaysa takım formdadır.")
                    
                    # 3. BAR CHART (Hücum Gücü)
                    fig_bar = go.Figure(data=[
                        go.Bar(name='Gol Beklentisi (xG)', x=[ev, dep], y=[res['ev_xg'], res['dep_xg']], marker_color='#29B6F6'),
                        go.Bar(name='Şut Ortalaması', x=[ev, dep], y=[res['ev_sut'], res['dep_sut']], marker_color='#FFA726')
                    ])
                    fig_bar.update_layout(title="Hücum Gücü (xG ve Şut)", barmode='group', paper_bgcolor='rgba(0,0,0,0)', font={'color':'white'})
                    st.plotly_chart(fig_bar, use_container_width=True)

                    # 4. YORUM KUTUSU
                    st.markdown(f"""
                    <div class="analysis-box">
                        <h4 style="color:#00E676;">🎙️ YAPAY ZEKA YORUMU</h4>
                        <p>Verilere göre <b>{ev}</b> son maçlarda ortalama <b>{np.mean(res['ev_trend']):.1f}</b> gol atma başarısı gösterdi. 
                        <b>{dep}</b> ise deplasmanlarda ortalama <b>{res['dep_sut']:.1f}</b> şut çekiyor.</p>
                        <p>Matematiksel model, <b>%{res['ms1']:.1f}</b> ihtimalle ev sahibini öne çıkarıyor. 
                        Gollü bir maç olması muhtemel (%{res['ust']:.1f} Üst ihtimali).</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.warning("Bu takımlar için henüz yeterli veri birikmemiş (Sezon başı olabilir).")
        else:
            st.error("Seçilen lig için veri dosyasında takım bulunamadı. Lig başlamamış olabilir.")
    else:
        st.error("Veri kaynağına bağlanılamadı. İnternet bağlantınızı kontrol edin veya daha sonra deneyin.")

# ================= SEKME 2: RAW VERİ =================
with tab2:
    st.markdown("### 📝 HAM VERİ İSTATİSTİKLERİ")
    if df is not None:
        st.dataframe(df.tail(20), use_container_width=True)
    else:
        st.info("Veri yüklenemedi.")

# ================= SEKME 3: ASİSTAN =================
with tab3:
    st.markdown("### 🤖 ASİSTAN JARVIS")
    if "messages" not in st.session_state: st.session_state.messages = [{"role": "assistant", "content": "Analizler hazır! Ne sormak istersin?"}]
    for msg in st.session_state.messages: st.chat_message(msg["role"]).write(msg["content"])
    if prompt := st.chat_input("Yaz bakalım..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        st.chat_message("assistant").write("Verileri analiz edip en doğru tahmini yapmaya çalışıyorum.")
