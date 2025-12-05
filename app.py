import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.graph_objects as go
import datetime

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Futbol Kahini Pro", page_icon="⚽", layout="wide")

# --- CSS (GÖRÜNÜM AYARLARI) ---
st.markdown("""
<style>
    /* Ana Arka Plan */
    .stApp { background-color: #0E1117; color: #E0E0E0; }
    
    /* Yazı Renkleri */
    h1, h2, h3 { color: #00E676 !important; font-family: 'Arial', sans-serif; }
    p, label, span, div { color: #CFD8DC; }
    
    /* İstatistik Kartları */
    .stat-card {
        background-color: #1F2937; 
        padding: 15px; 
        border-radius: 10px; 
        border: 1px solid #374151;
        text-align: center;
        margin-bottom: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    
    .big-score { font-size: 28px; font-weight: bold; color: #00E676; margin: 5px 0; }
    .card-title { font-size: 13px; color: #B0BEC5; text-transform: uppercase; letter-spacing: 1px; font-weight: bold; }
    
    /* Açıklama Kutusu (Grafik Yanı) */
    .desc-box {
        background-color: #263238;
        border-left: 4px solid #00E676;
        padding: 15px;
        border-radius: 5px;
        font-size: 14px;
        line-height: 1.5;
        color: white !important;
    }

    /* Tablo ve Buton */
    div[data-testid="stDataFrame"] { border: 1px solid #333; }
    .stButton>button { 
        background-color: #00E676; color: black; font-weight: bold; border-radius: 8px; height: 50px; border: none; width: 100%;
    }
    .stButton>button:hover { background-color: #00C853; color: white; }
    
    /* Sekme Renkleri */
    .stTabs [aria-selected="true"] { background-color: #00E676; color: black; }
</style>
""", unsafe_allow_html=True)

# --- VERİ SETLERİ ---
lig_kodlari = {
    "🇹🇷 Türkiye Süper Lig": "T1.csv", "🇬🇧 İngiltere Premier": "E0.csv", 
    "🇪🇸 İspanya La Liga": "SP1.csv", "🇩🇪 Almanya Bundesliga": "D1.csv", 
    "🇮🇹 İtalya Serie A": "I1.csv", "🇫🇷 Fransa Ligue 1": "F1.csv"
}

takim_duzeltme = {
    "Fenerbahce": "Fenerbahçe", "Galatasaray": "Galatasaray", "Besiktas": "Beşiktaş", "Trabzonspor": "Trabzonspor",
    "Buyuksehyr": "Başakşehir", "Man City": "Man City", "Man United": "Man Utd",
    "Real Madrid": "R. Madrid", "Barcelona": "Barcelona", "Bayern Munich": "Bayern",
    "Dortmund": "Dortmund", "Paris SG": "PSG", "Inter": "Inter", "Milan": "Milan", "Juventus": "Juve"
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

# --- PUAN DURUMU ---
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

# --- GÜÇLÜ ANALİZ MOTORU ---
def analiz_motoru(ev, dep, df):
    ev_stats = df[df['HomeTeam'] == ev]
    dep_stats = df[df['AwayTeam'] == dep]
    if len(ev_stats) < 2 or len(dep_stats) < 2: return None

    # 1. TEMEL İSTATİSTİKLER
    ev_gol_at = ev_stats['FTHG'].mean()
    dep_gol_at = dep_stats['FTAG'].mean()
    
    # 2. BASKI GÜCÜ (Şut ve İsabetli Şut Verisi Varsa)
    ev_baski = 50 # Varsayılan
    dep_baski = 50
    if 'HS' in df.columns and 'HST' in df.columns:
        # Şut sayısı + (İsabetli Şut * 2) bize baskı gücünü verir
        ev_score = ev_stats['HS'].mean() + (ev_stats['HST'].mean() * 2)
        dep_score = dep_stats['AS'].mean() + (dep_stats['AST'].mean() * 2)
        toplam = ev_score + dep_score
        ev_baski = (ev_score / toplam) * 100
        dep_baski = (dep_score / toplam) * 100

    # 3. KORNER ANALİZİ
    ev_korner = 0
    dep_korner = 0
    if 'HC' in df.columns:
        ev_korner = ev_stats['HC'].mean()
        dep_korner = dep_stats['AC'].mean()
    toplam_korner = ev_korner + dep_korner
    
    # 4. TAHMİNLER
    toplam_gol_beklenti = (ev_gol_at + dep_gol_at)
    
    skor_ev = int(round(ev_gol_at * 1.1)) # Hafif ev sahibi avantajı
    skor_dep = int(round(dep_gol_at * 0.9))
    
    kg = "VAR" if (ev_gol_at > 0.8 and dep_gol_at > 0.8) else "YOK"
    alt_ust = "2.5 ÜST" if toplam_gol_beklenti >= 2.5 else "2.5 ALT"
    
    # İbre
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
st.title("🦁 FUTBOL KAHİNİ MERKEZİ")

tab_analiz, tab_puan, tab_live, tab_chat = st.tabs(["📊 DETAYLI ANALİZ", "🏆 PUAN DURUMU", "📺 CANLI SKOR", "🤖 ASİSTAN"])

# ================= SEKME 1: GÖRSEL ANALİZ =================
with tab_analiz:
    st.markdown("### 🕵️‍♂️ MAÇ ANALİZ ROBOTU")
    
    c1, c2, c3 = st.columns([2,2,2])
    with c1: secilen_lig = st.selectbox("LİG SEÇ", list(lig_kodlari.keys()))
    df = veri_yukle(secilen_lig)
    
    if df is not None:
        takimlar = sorted(df['HomeTeam'].unique())
        with c2: ev = st.selectbox("EV SAHİBİ", takimlar)
        with c3: dep = st.selectbox("DEPLASMAN", takimlar, index=1)
        
        if st.button("DETAYLI ANALİZ ET 🚀"):
            res = analiz_motoru(ev, dep, df)
            
            if res:
                st.divider()
                
                # --- KISIM 1: ÖZET KARTLARI ---
                k1, k2, k3, k4 = st.columns(4)
                with k1:
                    st.markdown(f"""<div class="stat-card"><div class="card-title">SKOR TAHMİNİ</div><div class="big-score">{res['skor']}</div></div>""", unsafe_allow_html=True)
                with k2:
                    st.markdown(f"""<div class="stat-card"><div class="card-title">KAZANMA ŞANSI</div><div class="big-score">% {res['ibre']:.0f}</div></div>""", unsafe_allow_html=True)
                with k3:
                    st.markdown(f"""<div class="stat-card"><div class="card-title">GOL BARAJI</div><div class="big-score" style="font-size:22px;">{res['alt_ust']}</div></div>""", unsafe_allow_html=True)
                with k4:
                    st.markdown(f"""<div class="stat-card"><div class="card-title">TOPLAM KORNER</div><div class="big-score">{res['toplam_korner']:.1f}</div></div>""", unsafe_allow_html=True)

                st.divider()

                # --- KISIM 2: GRAFİKLER VE AÇIKLAMALAR ---
                st.markdown("### 📈 GRAFİKSEL DETAYLAR")

                # A) BASKI GRAFİĞİ (Bar Chart)
                g1, g2 = st.columns([2, 1])
                with g1:
                    fig_baski = go.Figure()
                    fig_baski.add_trace(go.Bar(y=[ev], x=[res['ev_baski']], orientation='h', name=ev, marker_color='#00E676'))
                    fig_baski.add_trace(go.Bar(y=[dep], x=[res['dep_baski']], orientation='h', name=dep, marker_color='#FF5252'))
                    fig_baski.update_layout(title="Sahada Kim Daha Baskın?", barmode='stack', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font={'color':'white'}, height=200)
                    st.plotly_chart(fig_baski, use_container_width=True)
                with g2:
                    st.markdown("**💡 BASKI ANALİZİ**")
                    dominant = ev if res['ev_baski'] > res['dep_baski'] else dep
                    st.markdown(f"""
                    <div class="desc-box">
                    Bu grafik takımların şut ve isabetli şut sayılarına göre hesaplanır.<br><br>
                    Şu an verilere göre <b>{dominant}</b> rakip kaleyi daha çok yokluyor ve oyunu domine etmeye daha yakın.
                    </div>
                    """, unsafe_allow_html=True)

                # B) RADAR GRAFİĞİ (Güç Dağılımı)
                g3, g4 = st.columns([1, 2])
                with g4:
                    st.markdown("**💡 GÜÇ KARŞILAŞTIRMASI**")
                    st.markdown(f"""
                    <div class="desc-box">
                    <ul>
                    <li><b>Hücum:</b> {ev if res['ev_gol'] > res['dep_gol'] else dep} gol yollarında daha etkili.</li>
                    <li><b>Korner:</b> Maç başına {ev} ortalama {res['ev_korner']:.1f}, {dep} ortalama {res['dep_korner']:.1f} korner kullanıyor.</li>
                    <li><b>Sonuç:</b> {res['alt_ust']} ihtimali yüksek görünüyor.</li>
                    </ul>
                    </div>
                    """, unsafe_allow_html=True)
                with g3:
                    categories = ['Hücum', 'Korner', 'Baskı', 'Gol Beklentisi']
                    fig_radar = go.Figure()
                    fig_radar.add_trace(go.Scatterpolar(
                        r=[res['ev_gol']*20, res['ev_korner']*10, res['ev_baski'], res['ev_gol']*25],
                        theta=categories, fill='toself', name=ev, line_color='#00E676'
                    ))
                    fig_radar.add_trace(go.Scatterpolar(
                        r=[res['dep_gol']*20, res['dep_korner']*10, res['dep_baski'], res['dep_gol']*25],
                        theta=categories, fill='toself', name=dep, line_color='#FF5252'
                    ))
                    fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font={'color':'white'}, height=250, margin=dict(t=20, b=20, l=20, r=20))
                    st.plotly_chart(fig_radar, use_container_width=True)
            else:
                st.error("Veri yetersiz.")

# ================= SEKME 2: PUAN DURUMU =================
with tab_puan:
    st.markdown(f"### 🏆 {secilen_lig} PUAN DURUMU")
    if df is not None:
        puan_df = puan_durumu_hesapla(df)
        st.dataframe(puan_df, use_container_width=True)

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
        # Basit cevap
        cevap = "Analiz sekmesinden detaylara bakabilirsin."
        if "naber" in prompt.lower(): cevap = "İyiyim, sen?"
        st.chat_message("assistant").write(cevap)
        st.session_state.messages.append({"role": "assistant", "content": cevap})
