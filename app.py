import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import datetime

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Futbol Kahini Masterclass", page_icon="🧠", layout="wide")

# --- CSS (NEON & PRO TASARIM) ---
st.markdown("""
<style>
    .stApp { background-color: #050505; color: #E0E0E0; }
    h1, h2, h3, h4 { color: #00E676 !important; font-family: 'Arial Black', sans-serif; text-transform: uppercase; letter-spacing: 1px; }
    
    /* NEON SEÇİM KUTULARI */
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
    .metric-sub { font-size: 11px; color: #00E676; }

    /* TAKTİK KARTLARI */
    .tactic-box {
        background-color: #1E1E1E; padding: 20px; border-radius: 12px; border: 1px solid #333; margin-top: 10px;
    }
    .tactic-header { color: #00E676; font-weight: bold; font-size: 18px; border-bottom: 1px solid #444; padding-bottom: 10px; margin-bottom: 10px; }
    .tactic-text { font-size: 15px; line-height: 1.6; color: #ddd; }
    
    /* Canlı Pencere Başlığı (Küçük) */
    .live-small { font-size: 14px; background: #222; padding: 5px 10px; border-radius: 5px; border-left: 3px solid #00E676; color: white; margin-bottom: 5px;}

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

# --- GELİŞMİŞ TAKTİK MOTORU ---
def taktik_analiz(stats, taraf="Ev"):
    gol_at = stats['FTHG'].mean() if taraf == "Ev" else stats['FTAG'].mean()
    gol_ye = stats['FTAG'].mean() if taraf == "Ev" else stats['FTHG'].mean()
    
    # Oyun Karakteri Çıkarımı
    stil = "Dengeli / Kontrollü"
    dizilis = "4-4-2 (Klasik)"
    
    if gol_at > 2.0 and gol_ye < 1.0:
        stil = "Dominant Hücum & Yüksek Pres"
        dizilis = "4-3-3 (Ofansif)"
    elif gol_at > 1.5 and gol_ye > 1.5:
        stil = "Kaotik / Gol Düellocusu"
        dizilis = "3-5-2 (Riskli)"
    elif gol_at < 1.0 and gol_ye < 1.0:
        stil = "Otobüs (Katı Savunma)"
        dizilis = "5-4-1 (Defansif)"
    elif gol_at < 1.0 and gol_ye > 1.5:
        stil = "Kırılgan / Savunma Zaafiyeti"
        dizilis = "4-5-1 (Direniş)"
        
    return stil, dizilis, gol_at, gol_ye

# --- İLK YARI / İKİNCİ YARI ANALİZİ ---
def yari_analizi(df, takim, taraf="Ev"):
    # Takımın o taraftaki maçları
    if taraf == "Ev":
        maclar = df[df['HomeTeam'] == takim]
        iy_gol = maclar['HTHG'].mean()
        iy_yenen = maclar['HTAG'].mean()
        ms_gol = maclar['FTHG'].mean()
    else:
        maclar = df[df['AwayTeam'] == takim]
        iy_gol = maclar['HTAG'].mean()
        iy_yenen = maclar['HTHG'].mean()
        ms_gol = maclar['FTAG'].mean()
        
    iy_orani = (iy_gol / ms_gol) * 100 if ms_gol > 0 else 0
    iy_karakter = "Hızlı Başlangıç" if iy_orani > 55 else ("İkinci Yarı Açılıyor" if iy_orani < 40 else "Dengeli Dağılım")
    
    return iy_gol, ms_gol - iy_gol, iy_karakter

# --- ANA ANALİZ FONKSİYONU ---
def detayli_analiz_motoru(ev, dep, df):
    ev_stats = df[df['HomeTeam'] == ev]
    dep_stats = df[df['AwayTeam'] == dep]
    if len(ev_stats) < 1 or len(dep_stats) < 1: return None

    # 1. TAKTİK PROFİL
    ev_stil, ev_dizilis, ev_g, ev_y = taktik_analiz(ev_stats, "Ev")
    dep_stil, dep_dizilis, dep_g, dep_y = taktik_analiz(dep_stats, "Dep")
    
    # 2. YARI ANALİZİ
    ev_iy, ev_iy2, ev_karakter = yari_analizi(df, ev, "Ev")
    dep_iy, dep_iy2, dep_karakter = yari_analizi(df, dep, "Dep")
    
    # 3. KORNER & KART (KAOS PUANI)
    ev_korner = ev_stats['HC'].mean() if 'HC' in df.columns else 4.5
    dep_korner = dep_stats['AC'].mean() if 'AC' in df.columns else 4.0
    ev_kart = ev_stats['HY'].mean() + ev_stats['AY'].mean() if 'HY' in df.columns else 2.0
    dep_kart = dep_stats['HY'].mean() + dep_stats['AY'].mean() if 'HY' in df.columns else 2.0
    
    kaos_puani = (ev_g + dep_g + ev_kart + dep_kart) * 10 # 100 üzerinden
    kaos_puani = min(100, kaos_puani)
    
    # 4. SKOR VE TAHMİN
    xG_toplam = ev_g + dep_g
    skor_ev = int(round(ev_g * 1.1))
    skor_dep = int(round(dep_g * 0.9))
    alt_ust = "2.5 ÜST" if xG_toplam >= 2.45 else "2.5 ALT"
    kg = "VAR" if (ev_g > 0.75 and dep_g > 0.75) else "YOK"
    
    fark = (ev_g * 1.5 - ev_y) - (dep_g * 1.5 - dep_y)
    ibre = 50 + (fark * 15)
    ibre = max(10, min(90, ibre))
    
    return {
        "ev": {"ad": ev, "stil": ev_stil, "dizilis": ev_dizilis, "iy": ev_iy, "iy2": ev_iy2, "karakter": ev_karakter},
        "dep": {"ad": dep, "stil": dep_stil, "dizilis": dep_dizilis, "iy": dep_iy, "iy2": dep_iy2, "karakter": dep_karakter},
        "mac": {"skor": f"{skor_ev}-{skor_dep}", "kg": kg, "alt_ust": alt_ust, "ibre": ibre, "kaos": kaos_puani, "korner": ev_korner+dep_korner}
    }

# --- ARAYÜZ ---
st.title("🦁 FUTBOL KAHİNİ: TACTICAL MASTERCLASS")

tab1, tab2, tab3 = st.tabs(["📊 ULTRA DETAYLI ANALİZ", "🏆 PUAN DURUMU", "🤖 ASİSTAN"])

# ================= SEKME 1: ANALİZ =================
with tab1:
    # 1. SEÇİM EKRANI
    c1, c2, c3 = st.columns([2, 2, 2])
    with c1: secilen_lig = st.selectbox("LİG SEÇİNİZ", list(lig_yapilandirma.keys()))
    df = veri_yukle(secilen_lig)
    
    if df is not None:
        takimlar = sorted(df['HomeTeam'].unique())
        with c2: ev = st.selectbox("EV SAHİBİ", takimlar)
        with c3: dep = st.selectbox("DEPLASMAN", takimlar, index=1)
        
        # --- CANLI PENCERE (KÜÇÜLTÜLMÜŞ) ---
        with st.expander("📡 Canlı Form Doğrulama (Tıkla Aç)", expanded=False):
            st.markdown("<div class='live-small'>Flashscore Canlı Verisi (Teyit Amaçlı)</div>", unsafe_allow_html=True)
            components.html(f"""<iframe src="{lig_yapilandirma[secilen_lig]['live']}" width="100%" height="300" frameborder="0" style="background:white;"></iframe>""", height=300)

        if st.button("ANALİZ LABORATUVARINI ÇALIŞTIR 🧬"):
            res = detayli_analiz_motoru(ev, dep, df)
            
            if res:
                # --- BÖLÜM 1: MAÇ KİMLİĞİ VE TAHMİN ---
                st.divider()
                k1, k2, k3, k4 = st.columns(4)
                with k1: st.markdown(f"""<div class="metric-card"><div class="metric-title">SKOR TAHMİNİ</div><div class="metric-value">{res['mac']['skor']}</div></div>""", unsafe_allow_html=True)
                with k2: st.markdown(f"""<div class="metric-card"><div class="metric-title">KAZANMA İHTİMALİ</div><div class="metric-value">% {res['mac']['ibre']:.0f}</div><div class="metric-sub">{res['ev']['ad']} Lehine</div></div>""", unsafe_allow_html=True)
                with k3: st.markdown(f"""<div class="metric-card"><div class="metric-title">TOPLAM GOL</div><div class="metric-value">{res['mac']['alt_ust']}</div></div>""", unsafe_allow_html=True)
                with k4: st.markdown(f"""<div class="metric-card"><div class="metric-title">KAOS PUANI (Kart+Gol)</div><div class="metric-value">{res['mac']['kaos']:.0f}/100</div></div>""", unsafe_allow_html=True)
                
                # --- BÖLÜM 2: TAKTİKSEL KİMLİK KARTLARI ---
                st.markdown("### 🛡️ TAKTİKSEL KİMLİK KARTLARI")
                t1, t2 = st.columns(2)
                
                with t1:
                    st.markdown(f"""
                    <div class="tactic-box" style="border-left: 4px solid #00E676;">
                        <div class="tactic-header">{res['ev']['ad']} (Ev Sahibi)</div>
                        <div class="tactic-text">
                        • <b>Oyun Stili:</b> {res['ev']['stil']}<br>
                        • <b>Önerilen Diziliş:</b> {res['ev']['dizilis']}<br>
                        • <b>Maç Karakteri:</b> {res['ev']['karakter']}<br>
                        • <b>Güçlü Yön:</b> İç saha baskısı ve erken goller.
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                with t2:
                    st.markdown(f"""
                    <div class="tactic-box" style="border-left: 4px solid #FF5252;">
                        <div class="tactic-header">{res['dep']['ad']} (Deplasman)</div>
                        <div class="tactic-text">
                        • <b>Oyun Stili:</b> {res['dep']['stil']}<br>
                        • <b>Önerilen Diziliş:</b> {res['dep']['dizilis']}<br>
                        • <b>Maç Karakteri:</b> {res['dep']['karakter']}<br>
                        • <b>Zayıf Yön:</b> Deplasman baskısını kırmakta zorlanabilirler.
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                # --- BÖLÜM 3: ZAMANLAMA VE GOL ANALİZİ (GRAFİKLER) ---
                st.markdown("### ⏱️ GOL ZAMANLAMASI & PERFORMANS")
                
                g1, g2 = st.columns(2)
                with g1:
                    # Donut Chart: Ev Sahibi Gol Dağılımı
                    labels = ['İlk Yarı Golleri', 'İkinci Yarı Golleri']
                    values = [res['ev']['iy'], res['ev']['iy2']]
                    fig_ev = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.6, marker_colors=['#00E676', '#008f51'])])
                    fig_ev.update_layout(title=f"{res['ev']['ad']} Gol Dağılımı", font=dict(color='white'), paper_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig_ev, use_container_width=True)
                
                with g2:
                    # Donut Chart: Deplasman Gol Dağılımı
                    values_dep = [res['dep']['iy'], res['dep']['iy2']]
                    fig_dep = go.Figure(data=[go.Pie(labels=labels, values=values_dep, hole=.6, marker_colors=['#FF5252', '#b33939'])])
                    fig_dep.update_layout(title=f"{res['dep']['ad']} Gol Dağılımı", font=dict(color='white'), paper_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig_dep, use_container_width=True)
                
                # --- BÖLÜM 4: DETAYLI YORUMCU ANALİZİ ---
                st.markdown("### 🎙️ YAPAY ZEKA TEKNİK ANALİZİ")
                st.markdown(f"""
                <div class="tactic-box">
                    <p><b>MAÇ SENARYOSU:</b><br>
                    Veriler ışığında, <b>{res['ev']['ad']}</b> takımının {res['ev']['stil'].lower()} anlayışıyla maça hızlı başlaması muhtemel ({res['ev']['karakter']}). 
                    Eğer ilk 30 dakikada gol bulurlarsa, <b>{res['dep']['ad']}</b> takımı risk alıp savunma arkasında boşluklar verebilir.</p>
                    
                    <p><b>KRİTİK BİLGİLER:</b><br>
                    - Maçın kaos puanı <b>{res['mac']['kaos']:.0f}</b>. {('Kart ve penaltı ihtimali yüksek sert bir maç.' if res['mac']['kaos']>60 else 'Daha sakin, taktiksel bir maç.')}<br>
                    - Beklenen toplam korner sayısı: <b>{res['mac']['korner']:.1f}</b>.</p>
                    
                    <p><b>SON SÖZ:</b><br>
                    İbre <b>%{res['mac']['ibre']:.0f}</b> oranında {res['ev']['ad']} tarafını gösteriyor. 
                    En mantıklı tercih <b>{res['mac']['alt_ust']}</b> ve <b>KG {res['mac']['kg']}</b> kombinasyonudur.</p>
                </div>
                """, unsafe_allow_html=True)

            else: st.error("Sezon başı verisi eksik.")

# ================= SEKME 2: PUAN DURUMU =================
with tab2:
    link = "https://www.livescore.bz"
    components.html(f"""<iframe src="{link}" width="100%" height="800" frameborder="0" style="background-color: white; border-radius: 10px;"></iframe>""", height=800, scrolling=True)

# ================= SEKME 3: ASİSTAN =================
with tab3:
    if "messages" not in st.session_state: st.session_state.messages = [{"role": "assistant", "content": "Selam! Maçları sorabilirsin."}]
    for msg in st.session_state.messages: st.chat_message(msg["role"]).write(msg["content"])
    if prompt := st.chat_input("Mesaj yaz..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        st.chat_message("assistant").write("Analiz sekmesinden detaylara bakabilirsin.")
