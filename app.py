import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.graph_objects as go
import datetime

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Futbol Kahini Pro", page_icon="⚽", layout="wide")

# --- CSS (NEON VE TABLO TASARIMI) ---
st.markdown("""
<style>
    /* Ana Arka Plan */
    .stApp { background-color: #0E1117; color: #E0E0E0; }
    
    /* BAŞLIKLAR - FOSFORLU YEŞİL */
    h1, h2, h3, h4 { color: #00E676 !important; font-family: 'Arial Black', sans-serif; text-transform: uppercase; letter-spacing: 1px; }
    
    /* --- SEÇİM KUTULARI (NEON) --- */
    .stSelectbox label p { font-size: 18px !important; color: #00E676 !important; font-weight: bold !important; }
    div[data-baseweb="select"] > div {
        background-color: #1F2937 !important; 
        border: 2px solid #00E676 !important; 
        color: white !important;
        border-radius: 8px !important;
    }
    div[data-baseweb="select"] span { color: #00E676 !important; font-weight: bold !important; font-size: 16px !important; }
    div[data-baseweb="select"] svg { fill: #00E676 !important; }
    
    /* İstatistik Kartları */
    .stat-card {
        background-color: #1F2937; padding: 15px; border-radius: 10px; border: 1px solid #374151;
        text-align: center; margin-bottom: 10px; box-shadow: 0 4px 10px rgba(0, 230, 118, 0.1); /* Hafif yeşil gölge */
    }
    .big-score { font-size: 28px; font-weight: bold; color: #00E676; margin: 5px 0; text-shadow: 0 0 10px rgba(0,230,118,0.5); }
    .card-title { font-size: 13px; color: #B0BEC5; text-transform: uppercase; letter-spacing: 1px; font-weight: bold; }
    
    /* Açıklama Kutusu */
    .desc-box {
        background-color: #263238; border-left: 4px solid #00E676; padding: 15px;
        border-radius: 5px; font-size: 14px; line-height: 1.5; color: white !important;
    }

    /* Tablo ve Buton */
    .stDataFrame { border: 1px solid #333; }
    .stButton>button { 
        background-color: #00E676; color: black !important; font-weight: 900 !important; 
        border-radius: 8px; height: 55px; border: 2px solid #00C853; width: 100%; font-size: 20px !important;
        box-shadow: 0 0 15px rgba(0, 230, 118, 0.4);
    }
    .stButton>button:hover { background-color: #00C853; color: white !important; transform: scale(1.02); }
    
    /* Sekme Renkleri */
    .stTabs [aria-selected="true"] { background-color: #00E676; color: black !important; font-weight: bold; border-radius: 5px; }
</style>
""", unsafe_allow_html=True)

# --- VERİ SETLERİ (GENİŞLETİLMİŞ LİSTE) ---
# Sözlük sıralaması Python 3.7+ itibariyle korunur. En üste önemlileri koyduk.
lig_kodlari = {
    # --- VİTRİN LİGLERİ ---
    "🇹🇷 Türkiye Süper Lig": "T1.csv",
    "🇬🇧 İngiltere Premier": "E0.csv", 
    "🇪🇸 İspanya La Liga": "SP1.csv",
    "🇩🇪 Almanya Bundesliga": "D1.csv", 
    "🇮🇹 İtalya Serie A": "I1.csv",
    "🇫🇷 Fransa Ligue 1": "F1.csv",
    # --- DİĞER AVRUPA ---
    "🇳🇱 Hollanda Eredivisie": "N1.csv",
    "🇵🇹 Portekiz Liga NOS": "P1.csv",
    "🇧🇪 Belçika Pro League": "B1.csv",
    "🏴󠁧󠁢󠁳󠁣󠁴󠁿 İskoçya Premiership": "SC0.csv",
    "🇬🇷 Yunanistan Süper Lig": "G1.csv"
}

takim_duzeltme = {
    "Fenerbahce": "Fenerbahçe", "Galatasaray": "Galatasaray", "Besiktas": "Beşiktaş", "Trabzonspor": "Trabzonspor",
    "Buyuksehyr": "Başakşehir", "Man City": "Man City", "Man United": "Man Utd",
    "Real Madrid": "R. Madrid", "Barcelona": "Barcelona", "Bayern Munich": "Bayern",
    "Dortmund": "Dortmund", "Paris SG": "PSG", "Inter": "Inter", "Milan": "Milan", "Juventus": "Juve",
    "Benfica": "Benfica", "Porto": "Porto", "Ajax": "Ajax", "PSV Eindhoven": "PSV", "Celtic": "Celtic"
}

# --- VERİ YÜKLEME ---
@st.cache_data(ttl=3600)
def veri_yukle(lig_ad):
    ana_url = "https://www.football-data.co.uk/mmz4281/2425/"
    dosya = lig_kodlari[lig_ad]
    try:
        url = ana_url + dosya
        df = pd.read_csv(url)
        df = df.dropna(subset=['FTR'])
        df['HomeTeam'] = df['HomeTeam'].replace(takim_duzeltme)
        df['AwayTeam'] = df['AwayTeam'].replace(takim_duzeltme)
        return df
    except: return None

# --- PUAN DURUMU HESAPLAMA ---
def puan_durumu_hesapla(df):
    takimlar = df['HomeTeam'].unique()
    puan_tablosu = []
    for t in takimlar:
        ev_mac = df[df['HomeTeam'] == t]
        dep_mac = df[df['AwayTeam'] == t]
        O = len(ev_mac) + len(dep_mac)
        G = len(ev_mac[ev_mac['FTR'] == 'H']) + len(dep_mac[dep_mac['FTR'] == 'A'])
        B = len(ev_mac[ev_mac['FTR'] == 'D']) + len(dep_mac[dep_mac['FTR'] == 'D'])
        M = len(ev_mac[ev_mac['FTR'] == 'A']) + len(dep_mac[dep_mac['FTR'] == 'H'])
        AV = (ev_mac['FTHG'].sum() + dep_mac['FTAG'].sum()) - (ev_mac['FTAG'].sum() + dep_mac['FTHG'].sum())
        P = (G * 3) + B
        puan_tablosu.append({"Takım": t, "O": O, "G": G, "B": B, "M": M, "AV": int(AV), "P": P})
    df_puan = pd.DataFrame(puan_tablosu).sort_values(by=['P', 'AV'], ascending=False).reset_index(drop=True)
    df_puan.index += 1
    return df_puan

# --- ANALİZ MOTORU ---
def analiz_motoru(ev, dep, df):
    ev_stats = df[df['HomeTeam'] == ev]
    dep_stats = df[df['AwayTeam'] == dep]
    if len(ev_stats) < 2 or len(dep_stats) < 2: return None

    # Veriler
    ev_gol_at = ev_stats['FTHG'].mean()
    dep_gol_at = dep_stats['FTAG'].mean()
    
    # Baskı Gücü
    ev_baski = 50; dep_baski = 50
    if 'HS' in df.columns and 'HST' in df.columns:
        ev_score = ev_stats['HS'].mean() + (ev_stats['HST'].mean() * 2)
        dep_score = dep_stats['AS'].mean() + (dep_stats['AST'].mean() * 2)
        toplam = ev_score + dep_score
        ev_baski = (ev_score / toplam) * 100
        dep_baski = (dep_score / toplam) * 100

    # Korner
    ev_korner = 0; dep_korner = 0
    if 'HC' in df.columns:
        ev_korner = ev_stats['HC'].mean()
        dep_korner = dep_stats['AC'].mean()
    toplam_korner = ev_korner + dep_korner
    
    # Tahminler
    toplam_gol_beklenti = (ev_gol_at + dep_gol_at)
    skor_ev = int(round(ev_gol_at * 1.1))
    skor_dep = int(round(dep_gol_at * 0.9))
    kg = "VAR" if (ev_gol_at > 0.8 and dep_gol_at > 0.8) else "YOK"
    alt_ust = "2.5 ÜST" if toplam_gol_beklenti >= 2.5 else "2.5 ALT"
    
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
st.title("🦁 FUTBOL KAHİNİ GLOBAL")

tab_analiz, tab_puan, tab_live, tab_chat = st.tabs(["📊 DETAYLI ANALİZ", "🏆 PUAN DURUMU", "📺 CANLI SKOR", "🤖 ASİSTAN"])

# ================= SEKME 1: ANALİZ =================
with tab_analiz:
    st.markdown("### 🕵️‍♂️ MAÇ ANALİZ ROBOTU")
    
    c1, c2, c3 = st.columns([2,2,2])
    with c1: secilen_lig = st.selectbox("LİG SEÇİNİZ", list(lig_kodlari.keys()))
    df = veri_yukle(secilen_lig)
    
    if df is not None:
        takimlar = sorted(df['HomeTeam'].unique())
        with c2: ev = st.selectbox("EV SAHİBİ TAKIM", takimlar)
        with c3: dep = st.selectbox("DEPLASMAN TAKIM", takimlar, index=1)
        
        st.markdown("")
        if st.button("ANALİZİ BAŞLAT 🚀"):
            res = analiz_motoru(ev, dep, df)
            
            if res:
                st.divider()
                # KARTLAR
                k1, k2, k3, k4 = st.columns(4)
                with k1: st.markdown(f"""<div class="stat-card"><div class="card-title">SKOR TAHMİNİ</div><div class="big-score">{res['skor']}</div></div>""", unsafe_allow_html=True)
                with k2: st.markdown(f"""<div class="stat-card"><div class="card-title">KAZANMA ŞANSI</div><div class="big-score">% {res['ibre']:.0f}</div></div>""", unsafe_allow_html=True)
                with k3: st.markdown(f"""<div class="stat-card"><div class="card-title">GOL BARAJI</div><div class="big-score" style="font-size:22px;">{res['alt_ust']}</div></div>""", unsafe_allow_html=True)
                with k4: st.markdown(f"""<div class="stat-card"><div class="card-title">TOPLAM KORNER</div><div class="big-score">{res['toplam_korner']:.1f}</div></div>""", unsafe_allow_html=True)

                st.divider()
                st.markdown("### 📈 GRAFİKSEL DETAYLAR")

                # BASKI GRAFİĞİ
                g1, g2 = st.columns([2, 1])
                with g1:
                    fig_baski = go.Figure()
                    fig_baski.add_trace(go.Bar(y=[ev], x=[res['ev_baski']], orientation='h', name=ev, marker_color='#00E676'))
                    fig_baski.add_trace(go.Bar(y=[dep], x=[res['dep_baski']], orientation='h', name=dep, marker_color='#FF5252'))
                    fig_baski.update_layout(title="Sahada Kim Daha Baskın?", barmode='stack', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font={'color':'white'}, height=200)
                    st.plotly_chart(fig_baski, use_container_width=True)
                with g2:
                    dominant = ev if res['ev_baski'] > res['dep_baski'] else dep
                    st.markdown(f"""<div class="desc-box"><b>💡 BASKI ANALİZİ</b><br>Şu an verilere göre <b>{dominant}</b> takımı hücumda daha çok şut çekiyor ve oyunu rakip sahaya yıkıyor.</div>""", unsafe_allow_html=True)

                # RADAR GRAFİĞİ
                g3, g4 = st.columns([1, 2])
                with g4:
                    st.markdown(f"""<div class="desc-box"><b>💡 GÜÇ KARŞILAŞTIRMASI</b><br><ul><li><b>Hücum:</b> {ev if res['ev_gol'] > res['dep_gol'] else dep} gol yollarında daha etkili.</li><li><b>Korner:</b> Maç başına {res['toplam_korner']:.1f} korner bekleniyor.</li></ul></div>""", unsafe_allow_html=True)
                with g3:
                    categories = ['Hücum', 'Korner', 'Baskı', 'Gol Beklentisi']
                    fig_radar = go.Figure()
                    fig_radar.add_trace(go.Scatterpolar(r=[res['ev_gol']*20, res['ev_korner']*10, res['ev_baski'], res['ev_gol']*25], theta=categories, fill='toself', name=ev, line_color='#00E676'))
                    fig_radar.add_trace(go.Scatterpolar(r=[res['dep_gol']*20, res['dep_korner']*10, res['dep_baski'], res['dep_gol']*25], theta=categories, fill='toself', name=dep, line_color='#FF5252'))
                    fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font={'color':'white'}, height=250, margin=dict(t=20, b=20, l=20, r=20))
                    st.plotly_chart(fig_radar, use_container_width=True)
            else: st.error("Sezon başı olduğu için veya veri eksik olduğu için analiz yapılamadı.")

# ================= SEKME 2: PUAN DURUMU (GÖRSEL ŞÖLEN) =================
with tab_puan:
    st.markdown(f"### 🏆 {secilen_lig} PUAN DURUMU")
    
    # 2. Lig seçimi (Buradan da değiştirebilsin)
    lig_puan = st.selectbox("Lig Değiştir:", list(lig_kodlari.keys()), key="puan_lig_sec")
    df_p = veri_yukle(lig_puan)
    
    if df_p is not None:
        puan_df = puan_durumu_hesapla(df_p)
        
        # TABLOYU GÖRSELLEŞTİRME (STYLING)
        st.dataframe(
            puan_df,
            use_container_width=True,
            column_config={
                "Takım": st.column_config.TextColumn("Takım Adı", width="medium"),
                "P": st.column_config.ProgressColumn(
                    "Puan",
                    help="Takımın topladığı puan",
                    format="%d",
                    min_value=0,
                    max_value=100, # Lig sonu max puan tahmini
                ),
                "AV": st.column_config.NumberColumn(
                    "Averaj",
                    format="%d"
                )
            },
            hide_index=False
        )
    else:
        st.error("Veri yüklenemedi.")

# ================= SEKME 3: CANLI SKOR =================
with tab_live:
    st.markdown("### 📺 CANLI MAÇ MERKEZİ")
    components.html("""<iframe src="https://www.livescore.bz" width="100%" height="600" frameborder="0" style="background-color: #eee; border-radius: 8px;"></iframe>""", height=600, scrolling=True)

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
