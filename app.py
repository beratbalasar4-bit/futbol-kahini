import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.graph_objects as go
import datetime

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Futbol Kahini Pro", page_icon="⚽", layout="wide")

# --- CSS (NEON VE PROFESYONEL) ---
st.markdown("""
<style>
    /* Ana Arka Plan */
    .stApp { background-color: #0E1117; color: #E0E0E0; }
    
    /* BAŞLIKLAR */
    h1, h2, h3, h4 { color: #00E676 !important; font-family: 'Arial Black', sans-serif; text-transform: uppercase; letter-spacing: 1px; }
    
    /* SEÇİM KUTULARI */
    .stSelectbox label p { font-size: 18px !important; color: #00E676 !important; font-weight: bold !important; }
    div[data-baseweb="select"] > div { background-color: #1F2937 !important; border: 2px solid #00E676 !important; color: white !important; border-radius: 8px !important; }
    div[data-baseweb="select"] span { color: #00E676 !important; font-weight: bold !important; font-size: 16px !important; }
    div[data-baseweb="select"] svg { fill: #00E676 !important; }
    
    /* İstatistik Kartları */
    .stat-card { background-color: #1F2937; padding: 15px; border-radius: 10px; border: 1px solid #374151; text-align: center; margin-bottom: 10px; box-shadow: 0 4px 10px rgba(0, 230, 118, 0.1); }
    .big-score { font-size: 28px; font-weight: bold; color: #00E676; margin: 5px 0; text-shadow: 0 0 10px rgba(0,230,118,0.5); }
    .card-title { font-size: 13px; color: #B0BEC5; text-transform: uppercase; letter-spacing: 1px; font-weight: bold; }
    
    /* Canlı Form Penceresi Başlığı */
    .live-header { background: linear-gradient(90deg, #1F2937 0%, #00E676 100%); padding: 10px; border-radius: 5px; color: white; font-weight: bold; margin-top: 20px; }

    /* Buton */
    .stButton>button { background-color: #00E676; color: black !important; font-weight: 900 !important; border-radius: 8px; height: 55px; border: 2px solid #00C853; width: 100%; font-size: 20px !important; box-shadow: 0 0 15px rgba(0, 230, 118, 0.4); }
    .stButton>button:hover { background-color: #00C853; color: white !important; transform: scale(1.02); }
    
    /* Sekme */
    .stTabs [aria-selected="true"] { background-color: #00E676; color: black !important; font-weight: bold; border-radius: 5px; }
</style>
""", unsafe_allow_html=True)

# --- GENİŞLETİLMİŞ LİG VE VERİ LİNKLERİ ---
lig_yapilandirma = {
    "🇹🇷 Türkiye Süper Lig": {"csv": "T1.csv", "live": "https://www.flashscore.mobi/standings/W6BOzpK2/U3MvIVsA/#table/overall"},
    "🇬🇧 İngiltere Premier": {"csv": "E0.csv", "live": "https://www.flashscore.mobi/standings/dYlOSQ44/W6DOvJ92/#table/overall"},
    "🇪🇸 İspanya La Liga": {"csv": "SP1.csv", "live": "https://www.flashscore.mobi/standings/QVmLl54o/dG2SqPPf/#table/overall"},
    "🇩🇪 Almanya Bundesliga": {"csv": "D1.csv", "live": "https://www.flashscore.mobi/standings/W6BOzpK2/U3MvIVsA/#table/overall"}, # Linkler örnek, dinamik değişebilir
    "🇮🇹 İtalya Serie A": {"csv": "I1.csv", "live": "https://www.flashscore.mobi/standings/dYlOSQ44/W6DOvJ92/#table/overall"},
    "🇫🇷 Fransa Ligue 1": {"csv": "F1.csv", "live": "https://www.flashscore.mobi/standings/W6BOzpK2/U3MvIVsA/#table/overall"},
    "🇳🇱 Hollanda Eredivisie": {"csv": "N1.csv", "live": "https://www.flashscore.mobi"},
    "🇵🇹 Portekiz Liga NOS": {"csv": "P1.csv", "live": "https://www.flashscore.mobi"},
    "🇧🇪 Belçika Jupiler": {"csv": "B1.csv", "live": "https://www.flashscore.mobi"},
    "🏴󠁧󠁢󠁳󠁣󠁴󠁿 İskoçya Premiership": {"csv": "SC0.csv", "live": "https://www.flashscore.mobi"},
    "🇬🇷 Yunanistan Süper Lig": {"csv": "G1.csv", "live": "https://www.flashscore.mobi"}
}

takim_duzeltme = {
    "Fenerbahce": "Fenerbahçe", "Galatasaray": "Galatasaray", "Besiktas": "Beşiktaş", "Trabzonspor": "Trabzonspor",
    "Buyuksehyr": "Başakşehir", "Man City": "Man City", "Man United": "Man Utd",
    "Real Madrid": "R. Madrid", "Barcelona": "Barcelona", "Bayern Munich": "Bayern",
    "Dortmund": "Dortmund", "Paris SG": "PSG", "Inter": "Inter", "Milan": "Milan", "Juventus": "Juve",
    "Benfica": "Benfica", "Porto": "Porto", "Ajax": "Ajax"
}

# --- VERİ YÜKLEME VE AKILLI TARİH DÜZELTME ---
@st.cache_data(ttl=3600)
def veri_yukle(lig_ad):
    ana_url = "https://www.football-data.co.uk/mmz4281/2425/" 
    dosya = lig_yapilandirma[lig_ad]["csv"]
    try:
        url = ana_url + dosya
        df = pd.read_csv(url)
        df = df.dropna(subset=['FTR'])
        
        # Tarih formatı bazen DD/MM/YY bazen MM/DD/YY geliyor. Bunu zorluyoruz.
        # errors='coerce' hatalı tarihleri NaT yapar, sonra onları sileriz.
        df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
        df = df.dropna(subset=['Date']) 
        df = df.sort_values(by='Date') # Eskiden yeniye sırala
        
        df['HomeTeam'] = df['HomeTeam'].replace(takim_duzeltme)
        df['AwayTeam'] = df['AwayTeam'].replace(takim_duzeltme)
        return df
    except: return None

# --- ANALİZ MOTORU ---
def analiz_motoru(ev, dep, df):
    ev_stats = df[df['HomeTeam'] == ev]
    dep_stats = df[df['AwayTeam'] == dep]
    if len(ev_stats) < 1 or len(dep_stats) < 1: return None

    # İstatistikler
    ev_gol_at = ev_stats['FTHG'].mean()
    dep_gol_at = dep_stats['FTAG'].mean()
    
    # Baskı Gücü
    ev_baski = 50; dep_baski = 50
    if 'HS' in df.columns:
        ev_score = ev_stats['HS'].mean() + (ev_stats['HST'].mean() * 2)
        dep_score = dep_stats['AS'].mean() + (dep_stats['AST'].mean() * 2)
        toplam = ev_score + dep_score
        ev_baski = (ev_score / toplam) * 100
        dep_baski = (dep_score / toplam) * 100

    # Korner
    ev_korner = ev_stats['HC'].mean() if 'HC' in df.columns else 4.5
    dep_korner = dep_stats['AC'].mean() if 'AC' in df.columns else 4.0
    toplam_korner = ev_korner + dep_korner
    
    # Tahminler
    toplam_gol_beklenti = (ev_gol_at + dep_gol_at)
    skor_ev = int(round(ev_gol_at * 1.15))
    skor_dep = int(round(dep_gol_at * 0.9))
    kg = "VAR" if (ev_gol_at > 0.7 and dep_gol_at > 0.7) else "YOK"
    alt_ust = "2.5 ÜST" if toplam_gol_beklenti >= 2.4 else "2.5 ALT"
    
    fark = ev_baski - dep_baski
    ibre = 50 + (fark / 1.5)
    ibre = max(10, min(90, ibre))
    
    return {
        "skor": f"{skor_ev} - {skor_dep}", "kg": kg, "alt_ust": alt_ust,
        "ibre": ibre, "ev_baski": ev_baski, "dep_baski": dep_baski,
        "ev_korner": ev_korner, "dep_korner": dep_korner, "toplam_korner": toplam_korner,
        "ev_gol": ev_gol_at, "dep_gol": dep_gol_at
    }

# --- ARAYÜZ ---
st.title("🦁 FUTBOL KAHİNİ V23")

tab_analiz, tab_puan, tab_live, tab_chat = st.tabs(["📊 DETAYLI ANALİZ", "🏆 PUAN DURUMU", "📺 CANLI SKOR", "🤖 ASİSTAN"])

# ================= SEKME 1: HİBRİT ANALİZ =================
with tab_analiz:
    st.markdown("### 🕵️‍♂️ MAÇ ANALİZ MERKEZİ")
    
    c1, c2, c3 = st.columns([2,2,2])
    with c1: secilen_lig = st.selectbox("LİG SEÇİNİZ", list(lig_yapilandirma.keys()))
    df = veri_yukle(secilen_lig)
    
    if df is not None:
        takimlar = sorted(df['HomeTeam'].unique())
        with c2: ev = st.selectbox("EV SAHİBİ", takimlar)
        with c3: dep = st.selectbox("DEPLASMAN", takimlar, index=1)
        
        st.markdown("")
        if st.button("DETAYLI ANALİZ ET 🚀"):
            res = analiz_motoru(ev, dep, df)
            
            if res:
                st.divider()
                
                # --- YENİ BÖLÜM: CANLI FORM DOĞRULAMA PENCERESİ ---
                # CSV dosyaları gecikebilir, bu yüzden %100 doğru bilgi için canlı siteyi gömüyoruz.
                st.markdown("<div class='live-header'>📡 CANLI FORM VE KADRO DOĞRULAMA (Flashscore Mobil)</div>", unsafe_allow_html=True)
                st.caption("Veriler CSV dosyasından analiz edilir. %100 güncel son maçlar ve eksikler için aşağıdaki pencereyi kullanın.")
                
                # Mobil arayüz linki (Daha temiz görünür)
                canli_link = lig_yapilandirma[secilen_lig]["live"]
                components.html(f"""
                <iframe src="{canli_link}" width="100%" height="400" frameborder="0" style="background-color: white; border-radius: 10px; border: 2px solid #00E676;"></iframe>
                """, height=400)
                
                st.divider()

                # --- YAPAY ZEKA TAHMİNLERİ ---
                st.markdown("#### 🤖 YAPAY ZEKA TAHMİNLERİ")
                k1, k2, k3, k4 = st.columns(4)
                with k1: st.markdown(f"""<div class="stat-card"><div class="card-title">SKOR TAHMİNİ</div><div class="big-score">{res['skor']}</div></div>""", unsafe_allow_html=True)
                with k2: st.markdown(f"""<div class="stat-card"><div class="card-title">KAZANMA ŞANSI</div><div class="big-score">% {res['ibre']:.0f}</div></div>""", unsafe_allow_html=True)
                with k3: st.markdown(f"""<div class="stat-card"><div class="card-title">GOL BARAJI</div><div class="big-score" style="font-size:22px;">{res['alt_ust']}</div></div>""", unsafe_allow_html=True)
                with k4: st.markdown(f"""<div class="stat-card"><div class="card-title">KG (KARŞILIKLI)</div><div class="big-score" style="font-size:22px;">{res['kg']}</div></div>""", unsafe_allow_html=True)

                # --- GRAFİKLER ---
                g1, g2 = st.columns(2)
                with g1:
                    # Baskı Grafiği
                    fig_baski = go.Figure()
                    fig_baski.add_trace(go.Bar(y=[ev], x=[res['ev_baski']], orientation='h', name=ev, marker_color='#00E676'))
                    fig_baski.add_trace(go.Bar(y=[dep], x=[res['dep_baski']], orientation='h', name=dep, marker_color='#FF5252'))
                    fig_baski.update_layout(title="Baskı Gücü (Şut & İsabet)", barmode='stack', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font={'color':'white'}, height=250)
                    st.plotly_chart(fig_baski, use_container_width=True)
                
                with g2:
                     # Radar
                    categories = ['Hücum', 'Korner', 'Baskı', 'Gol Beklentisi']
                    fig_radar = go.Figure()
                    fig_radar.add_trace(go.Scatterpolar(r=[res['ev_gol']*20, res['ev_korner']*10, res['ev_baski'], res['ev_gol']*25], theta=categories, fill='toself', name=ev, line_color='#00E676'))
                    fig_radar.add_trace(go.Scatterpolar(r=[res['dep_gol']*20, res['dep_korner']*10, res['dep_baski'], res['dep_gol']*25], theta=categories, fill='toself', name=dep, line_color='#FF5252'))
                    fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font={'color':'white'}, height=250, margin=dict(t=20, b=20, l=20, r=20), title="Güç Dağılımı")
                    st.plotly_chart(fig_radar, use_container_width=True)

                # YORUM
                st.markdown(f"""
                <div class="desc-box">
                <b>💡 ANALİZ ÖZETİ:</b><br>
                <b>{ev}</b> evinde baskın oynuyor (Baskı Gücü: {res['ev_baski']:.0f}). 
                <b>{dep}</b> ise deplasmanlarda kontrollü. <br><br>
                Yapay zeka bu maçta <b>{res['alt_ust']}</b> ve <b>{res['kg']}</b> seçeneklerini mantıklı buluyor.
                </div>
                """, unsafe_allow_html=True)
            else: st.error("Veri yetersiz veya sezon başı.")

# ================= SEKME 2: PUAN DURUMU (IFRAME) =================
with tab_puan:
    st.markdown(f"### 🏆 GÜNCEL PUAN DURUMU")
    # Livescore masaüstü versiyonu puan durumu için daha iyidir
    link = "https://www.livescore.bz"
    components.html(f"""<iframe src="{link}" width="100%" height="800" frameborder="0" style="background-color: white; border-radius: 10px;"></iframe>""", height=800, scrolling=True)

# ================= SEKME 3: CANLI SKOR =================
with tab_live:
    st.markdown("### 📺 CANLI MAÇ MERKEZİ")
    components.html("""<iframe src="https://www.livescore.bz" width="100%" height="800" frameborder="0" style="background-color: white; border-radius: 8px;"></iframe>""", height=800, scrolling=True)

# ================= SEKME 4: ASİSTAN =================
with tab_chat:
    st.markdown("### 🤖 ASİSTAN JARVIS")
    if "messages" not in st.session_state: st.session_state.messages = [{"role": "assistant", "content": "Selam! Maçları sorabilirsin."}]
    for msg in st.session_state.messages: st.chat_message(msg["role"]).write(msg["content"])
    if prompt := st.chat_input("Mesaj yaz..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        cevap = "Analiz sekmesinden maçı seçip detaylara bakabilirsin."
        if "naber" in prompt.lower(): cevap = "İyiyim, sen?"
        st.chat_message("assistant").write(cevap)
        st.session_state.messages.append({"role": "assistant", "content": cevap})
