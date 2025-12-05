import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import datetime

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Futbol Kahini Manager", page_icon="⚽", layout="wide")

# --- CSS (TASARIM VE DÜZELTMELER) ---
st.markdown("""
<style>
    /* GENEL */
    .stApp { background-color: #050505; color: #E0E0E0; }
    h1, h2, h3, h4 { color: #00E676 !important; font-family: 'Arial Black', sans-serif; text-transform: uppercase; letter-spacing: 1px; }
    
    /* SEÇİM KUTULARI */
    .stSelectbox label p { font-size: 16px !important; color: #00E676 !important; font-weight: bold; }
    div[data-baseweb="select"] > div { background-color: #121212 !important; border: 1px solid #00E676 !important; color: white !important; }
    
    /* ANALİZ KUTULARI */
    .metric-card {
        background: linear-gradient(145deg, #1a1a1a, #121212);
        padding: 15px; border-radius: 10px; border-left: 5px solid #00E676;
        text-align: center; margin-bottom: 10px; box-shadow: 0 4px 15px rgba(0,230,118,0.1);
    }
    .metric-title { font-size: 12px; color: #aaa; text-transform: uppercase; letter-spacing: 1px; }
    .metric-value { font-size: 24px; font-weight: bold; color: white; margin-top: 5px; }

    /* TAKTİK VE YORUM KUTUSU (DÜZELTİLDİ: ARTIK KOD GİBİ GÖRÜNMÜYOR) */
    .tactic-box {
        background-color: #1E1E1E; 
        padding: 20px; 
        border-radius: 12px; 
        border: 1px solid #333; 
        margin-top: 10px;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important; /* Normal yazı tipi */
    }
    .tactic-header { color: #00E676; font-weight: bold; font-size: 18px; border-bottom: 1px solid #444; padding-bottom: 10px; margin-bottom: 10px; }
    .tactic-text { font-size: 16px; line-height: 1.6; color: #ddd; }
    
    /* --- FUTBOL SAHASI VE KADRO TASARIMI --- */
    .pitch-container {
        background: linear-gradient(0deg, #2E7D32 0%, #388E3C 50%, #2E7D32 100%); /* Çim Rengi */
        border: 4px solid white;
        border-radius: 10px;
        padding: 20px;
        position: relative;
        text-align: center;
        margin-top: 20px;
    }
    .pitch-line { border-top: 2px solid rgba(255,255,255,0.3); margin: 20px 0; }
    
    /* OYUNCU KARTI (FIFA STYLE) */
    .player-card-input input {
        text-align: center;
        font-weight: bold;
        color: black !important;
        background-color: #FFD700 !important; /* Altın Kart Rengi */
        border: 2px solid #DAA520;
        border-radius: 5px;
    }
    .player-label { font-size: 12px; color: white; font-weight: bold; margin-bottom: 2px; text-transform: uppercase; text-shadow: 1px 1px 2px black; }
    
    /* Sekme */
    .stTabs [aria-selected="true"] { background-color: #00E676; color: black !important; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- VERİ SETLERİ ---
lig_yapilandirma = {
    "🇹🇷 Türkiye Süper Lig": {"csv": "T1.csv", "live": "https://www.flashscore.mobi/standings/W6BOzpK2/U3MvIVsA/#table/overall"},
    "🇬🇧 İngiltere Premier": {"csv": "E0.csv", "live": "https://www.flashscore.mobi/standings/dYlOSQ44/W6DOvJ92/#table/overall"},
    "🇪🇸 İspanya La Liga": {"csv": "SP1.csv", "live": "https://www.flashscore.mobi/standings/QVmLl54o/dG2SqPPf/#table/overall"},
    "🇩🇪 Almanya Bundesliga": {"csv": "D1.csv", "live": "https://www.flashscore.mobi/standings/W6BOzpK2/U3MvIVsA/#table/overall"},
    "🇮🇹 İtalya Serie A": {"csv": "I1.csv", "live": "https://www.flashscore.mobi/standings/dYlOSQ44/W6DOvJ92/#table/overall"},
    "🇫🇷 Fransa Ligue 1": {"csv": "F1.csv", "live": "https://www.flashscore.mobi/standings/W6BOzpK2/U3MvIVsA/#table/overall"},
    "🇳🇱 Hollanda Eredivisie": {"csv": "N1.csv", "live": "https://www.flashscore.mobi"},
    "🇵🇹 Portekiz Liga NOS": {"csv": "P1.csv", "live": "https://www.flashscore.mobi"}
}

takim_duzeltme = {
    "Fenerbahce": "Fenerbahçe", "Galatasaray": "Galatasaray", "Besiktas": "Beşiktaş", "Trabzonspor": "Trabzonspor",
    "Buyuksehyr": "Başakşehir", "Man City": "Man City", "Man United": "Man Utd", "Real Madrid": "R. Madrid", 
    "Barcelona": "Barcelona", "Bayern Munich": "Bayern", "Dortmund": "Dortmund", "Paris SG": "PSG", 
    "Inter": "Inter", "Milan": "Milan", "Juventus": "Juve", "Benfica": "Benfica", "Porto": "Porto", "Ajax": "Ajax"
}

# --- VERİ YÜKLEME ---
@st.cache_data(ttl=3600)
def veri_yukle(lig_ad):
    ana_url = "https://www.football-data.co.uk/mmz4281/2425/" 
    dosya = lig_yapilandirma[lig_ad]["csv"]
    try:
        url = ana_url + dosya
        df = pd.read_csv(url)
        df = df.dropna(subset=['FTR'])
        df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
        df = df.sort_values(by='Date')
        df['HomeTeam'] = df['HomeTeam'].replace(takim_duzeltme)
        df['AwayTeam'] = df['AwayTeam'].replace(takim_duzeltme)
        return df
    except: return None

# --- TAKTİK MOTORU ---
def taktik_analiz(stats, taraf="Ev"):
    gol_at = stats['FTHG'].mean() if taraf == "Ev" else stats['FTAG'].mean()
    gol_ye = stats['FTAG'].mean() if taraf == "Ev" else stats['FTHG'].mean()
    stil = "Dengeli"
    if gol_at > 2.0: stil = "Hücum Futbolu"
    elif gol_ye < 0.8: stil = "Savunma Ağırlıklı"
    return stil, gol_at, gol_ye

# --- ANA ANALİZ ---
def detayli_analiz_motoru(ev, dep, df):
    ev_stats = df[df['HomeTeam'] == ev]
    dep_stats = df[df['AwayTeam'] == dep]
    if len(ev_stats) < 1 or len(dep_stats) < 1: return None

    ev_stil, ev_g, ev_y = taktik_analiz(ev_stats, "Ev")
    dep_stil, dep_g, dep_y = taktik_analiz(dep_stats, "Dep")
    
    # Kaos
    ev_kart = ev_stats['HY'].mean() + ev_stats['AY'].mean() if 'HY' in df.columns else 2.0
    dep_kart = dep_stats['HY'].mean() + dep_stats['AY'].mean() if 'HY' in df.columns else 2.0
    kaos = (ev_g + dep_g + ev_kart + dep_kart) * 10
    
    # Tahmin
    skor_ev = int(round(ev_g * 1.1))
    skor_dep = int(round(dep_g * 0.9))
    fark = (ev_g * 1.5 - ev_y) - (dep_g * 1.5 - dep_y)
    ibre = 50 + (fark * 15)
    ibre = max(10, min(90, ibre))
    alt_ust = "2.5 ÜST" if (ev_g + dep_g) >= 2.45 else "2.5 ALT"
    kg = "VAR" if (ev_g > 0.75 and dep_g > 0.75) else "YOK"

    return {
        "ev": {"ad": ev, "stil": ev_stil}, "dep": {"ad": dep, "stil": dep_stil},
        "mac": {"skor": f"{skor_ev}-{skor_dep}", "kg": kg, "alt_ust": alt_ust, "ibre": ibre, "kaos": kaos}
    }

# --- ARAYÜZ ---
st.title("🦁 FUTBOL KAHİNİ: MANAGER MODE")

tab1, tab2, tab3 = st.tabs(["📊 DETAYLI ANALİZ", "👕 KADRO KUR & TAKTİK", "🤖 ASİSTAN"])

# ================= SEKME 1: ANALİZ =================
with tab1:
    c1, c2, c3 = st.columns([2, 2, 2])
    with c1: secilen_lig = st.selectbox("LİG SEÇİNİZ", list(lig_yapilandirma.keys()))
    df = veri_yukle(secilen_lig)
    
    if df is not None:
        takimlar = sorted(df['HomeTeam'].unique())
        with c2: ev = st.selectbox("EV SAHİBİ", takimlar)
        with c3: dep = st.selectbox("DEPLASMAN", takimlar, index=1)
        
        with st.expander("📡 Canlı Form Doğrulama (Tıkla Aç)", expanded=False):
            st.caption("Veriler anlık Flashscore'dan çekilir.")
            components.html(f"""<iframe src="{lig_yapilandirma[secilen_lig]['live']}" width="100%" height="300" frameborder="0" style="background:white;"></iframe>""", height=300)

        if st.button("ANALİZ LABORATUVARINI ÇALIŞTIR 🧬"):
            res = detayli_analiz_motoru(ev, dep, df)
            
            if res:
                st.divider()
                k1, k2, k3, k4 = st.columns(4)
                with k1: st.markdown(f"""<div class="metric-card"><div class="metric-title">SKOR TAHMİNİ</div><div class="metric-value">{res['mac']['skor']}</div></div>""", unsafe_allow_html=True)
                with k2: st.markdown(f"""<div class="metric-card"><div class="metric-title">KAZANMA İHTİMALİ</div><div class="metric-value">% {res['mac']['ibre']:.0f}</div></div>""", unsafe_allow_html=True)
                with k3: st.markdown(f"""<div class="metric-card"><div class="metric-title">TOPLAM GOL</div><div class="metric-value">{res['mac']['alt_ust']}</div></div>""", unsafe_allow_html=True)
                with k4: st.markdown(f"""<div class="metric-card"><div class="metric-title">KG (KARŞILIKLI)</div><div class="metric-value">{res['mac']['kg']}</div></div>""", unsafe_allow_html=True)
                
                # YORUM ALANI (DÜZELTİLDİ: NORMAL YAZI TİPİ)
                st.markdown("### 🎙️ YAPAY ZEKA SENARYOSU")
                st.markdown(f"""
                <div class="tactic-box">
                    <div class="tactic-header">MAÇ HİKAYESİ</div>
                    <div class="tactic-text">
                        Verilere göre <b>{res['ev']['ad']}</b> sahaya <b>{res['ev']['stil']}</b> anlayışıyla çıkacak. 
                        Ev sahibi avantajını kullanarak maça hızlı başlamaları bekleniyor.
                        <br><br>
                        <b>{res['dep']['ad']}</b> ise deplasmanda <b>{res['dep']['stil']}</b> oynuyor. 
                        Maçın Kaos Puanı <b>{res['mac']['kaos']:.0f}/100</b>. 
                        Bu maçta {('kartların havada uçuşması' if res['mac']['kaos']>60 else 'taktiksel bir satranç')} izleyebiliriz.
                        <br><br>
                        <b>SONUÇ:</b> İbre {res['mac']['ibre']:.0f}% oranında {res['ev']['ad']} diyor. 
                        Ancak futbolda her zaman sürpriz ihtimali vardır.
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else: st.error("Sezon başı verisi eksik.")

# ================= SEKME 2: KADRO KURUCU (FIFA STYLE) =================
with tab2:
    st.markdown("### 👕 TEKNİK DİREKTÖR TAHTASI")
    st.caption("Aşağıdaki sahada kendi ilk 11'ini oluştur. Dizilişi seç ve oyuncu isimlerini yaz.")
    
    col_tac1, col_tac2 = st.columns([1, 3])
    
    with col_tac1:
        formation = st.selectbox("Diziliş Seç:", ["4-4-2", "4-3-3", "3-5-2", "4-2-3-1", "3-4-3"])
        st.info("💡 **İPUCU:** Oyuncu kutularına tıklayıp isimleri (Örn: Icardi, Tadic) kendin yazabilirsin.")
    
    with col_tac2:
        # SAHA TASARIMI
        st.markdown(f"""<div class="pitch-container">""", unsafe_allow_html=True)
        
        # --- KALECİ ---
        st.markdown('<div class="player-label">KALECİ (GK)</div>', unsafe_allow_html=True)
        c_gk = st.columns([1, 1, 1])
        with c_gk[1]: st.text_input("GK", placeholder="Kaleci", label_visibility="collapsed")
        
        st.markdown('<div class="pitch-line"></div>', unsafe_allow_html=True)
        
        # --- DEFANS ---
        st.markdown('<div class="player-label">DEFANS HATTI</div>', unsafe_allow_html=True)
        if formation.startswith("4"):
            d1, d2, d3, d4 = st.columns(4)
            with d1: st.text_input("LB", placeholder="Sol Bek", label_visibility="collapsed")
            with d2: st.text_input("CB1", placeholder="Stoper", label_visibility="collapsed")
            with d3: st.text_input("CB2", placeholder="Stoper", label_visibility="collapsed")
            with d4: st.text_input("RB", placeholder="Sağ Bek", label_visibility="collapsed")
        elif formation.startswith("3"):
            d1, d2, d3 = st.columns(3)
            with d1: st.text_input("CB1", placeholder="Stoper", label_visibility="collapsed")
            with d2: st.text_input("CB2", placeholder="Stoper", label_visibility="collapsed")
            with d3: st.text_input("CB3", placeholder="Stoper", label_visibility="collapsed")

        st.markdown('<div class="pitch-line"></div>', unsafe_allow_html=True)

        # --- ORTA SAHA ---
        st.markdown('<div class="player-label">ORTA SAHA</div>', unsafe_allow_html=True)
        if formation == "4-4-2":
            m1, m2, m3, m4 = st.columns(4)
            with m1: st.text_input("LM", placeholder="Sol Kanat", label_visibility="collapsed")
            with m2: st.text_input("CM1", placeholder="Merkez", label_visibility="collapsed")
            with m3: st.text_input("CM2", placeholder="Merkez", label_visibility="collapsed")
            with m4: st.text_input("RM", placeholder="Sağ Kanat", label_visibility="collapsed")
        elif formation == "4-3-3" or formation == "3-4-3":
            # 3'lü Orta Saha
            m1, m2, m3 = st.columns(3)
            with m1: st.text_input("CM1", placeholder="Merkez", label_visibility="collapsed")
            with m2: st.text_input("CDM", placeholder="Ön Libero", label_visibility="collapsed")
            with m3: st.text_input("CM2", placeholder="Merkez", label_visibility="collapsed")
        elif formation == "4-2-3-1" or formation == "3-5-2":
            # Kalabalık Orta Saha
            m1, m2, m3, m4, m5 = st.columns(5)
            with m1: st.text_input("M1", placeholder="Kanat/Bek", label_visibility="collapsed")
            with m2: st.text_input("M2", placeholder="Ort", label_visibility="collapsed")
            with m3: st.text_input("M3", placeholder="10 Numara", label_visibility="collapsed")
            with m4: st.text_input("M4", placeholder="Ort", label_visibility="collapsed")
            with m5: st.text_input("M5", placeholder="Kanat/Bek", label_visibility="collapsed")

        st.markdown('<div class="pitch-line"></div>', unsafe_allow_html=True)

        # --- FORVET ---
        st.markdown('<div class="player-label">HÜCUM HATTI</div>', unsafe_allow_html=True)
        if formation == "4-3-3" or formation == "3-4-3":
            f1, f2, f3 = st.columns(3)
            with f1: st.text_input("LW", placeholder="Sol Açık", label_visibility="collapsed")
            with f2: st.text_input("ST", placeholder="Golcü", label_visibility="collapsed")
            with f3: st.text_input("RW", placeholder="Sağ Açık", label_visibility="collapsed")
        elif formation == "4-2-3-1":
            f1, f2, f3 = st.columns([1,2,1]) # Tek forvet ortada
            with f2: st.text_input("ST", placeholder="Golcü", label_visibility="collapsed")
        else: # Çift Forvet (4-4-2, 3-5-2)
            f1, f2 = st.columns(2)
            with f1: st.text_input("ST1", placeholder="Golcü", label_visibility="collapsed")
            with f2: st.text_input("ST2", placeholder="Golcü", label_visibility="collapsed")

        st.markdown("</div>", unsafe_allow_html=True) # Pitch Container End

# ================= SEKME 3: ASİSTAN =================
with tab3:
    if "messages" not in st.session_state: st.session_state.messages = [{"role": "assistant", "content": "Selam! Maçları sorabilirsin."}]
    for msg in st.session_state.messages: st.chat_message(msg["role"]).write(msg["content"])
    if prompt := st.chat_input("Mesaj yaz..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        st.chat_message("assistant").write("Analiz sekmesinden detaylara bakabilirsin.")
