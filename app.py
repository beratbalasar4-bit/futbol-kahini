import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.graph_objects as go
import datetime

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Futbol Kahini Pro", page_icon="⚽", layout="wide")

# --- CSS (RENK VE GÖRÜNÜM DÜZELTME) ---
# Bu kod siteyi zorla 'Koyu Mod' yapar ve yazıları okunabilir kılar.
st.markdown("""
<style>
    /* Ana Arka Plan */
    .stApp { background-color: #0E1117; color: #E0E0E0; }
    
    /* Başlıklar */
    h1, h2, h3 { color: #00E676 !important; font-family: 'Arial', sans-serif; }
    p, label, span { color: #CFD8DC !important; }
    
    /* Kart Tasarımları (Arka planı ve yazısı garanti altına alındı) */
    .stat-card {
        background-color: #1F2937; 
        color: white;
        padding: 15px; 
        border-radius: 10px; 
        border: 1px solid #374151;
        text-align: center;
        margin-bottom: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.5);
    }
    
    .big-score { font-size: 32px; font-weight: bold; color: #00E676; margin: 5px 0; }
    .card-title { font-size: 14px; color: #B0BEC5; text-transform: uppercase; letter-spacing: 1px; }
    
    /* Tablo Tasarımı */
    div[data-testid="stDataFrame"] { border: 1px solid #333; border-radius: 5px; }
    
    /* Buton */
    .stButton>button { 
        background-color: #00E676; color: black; font-weight: bold; border-radius: 8px; height: 50px; border: none; width: 100%;
    }
    .stButton>button:hover { background-color: #00C853; color: white; }

    /* Sekme Başlıkları */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: #1F2937; border-radius: 5px; color: white; }
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

# --- PUAN DURUMU HESAPLAMA MOTORU (YENİ ÖZELLİK) ---
def puan_durumu_hesapla(df):
    takimlar = df['HomeTeam'].unique()
    puan_tablosu = []
    
    for t in takimlar:
        # İç Saha
        ev_mac = df[df['HomeTeam'] == t]
        ev_G = len(ev_mac[ev_mac['FTR'] == 'H'])
        ev_B = len(ev_mac[ev_mac['FTR'] == 'D'])
        ev_M = len(ev_mac[ev_mac['FTR'] == 'A'])
        ev_AG = ev_mac['FTHG'].sum()
        ev_YG = ev_mac['FTAG'].sum()
        
        # Deplasman
        dep_mac = df[df['AwayTeam'] == t]
        dep_G = len(dep_mac[dep_mac['FTR'] == 'A'])
        dep_B = len(dep_mac[dep_mac['FTR'] == 'D'])
        dep_M = len(dep_mac[dep_mac['FTR'] == 'H'])
        dep_AG = dep_mac['FTAG'].sum()
        dep_YG = dep_mac['FTHG'].sum()
        
        # Toplam
        O = len(ev_mac) + len(dep_mac)
        G = ev_G + dep_G
        B = ev_B + dep_B
        M = ev_M + dep_M
        AG = ev_AG + dep_AG
        YG = ev_YG + dep_YG
        AV = AG - YG
        P = (G * 3) + B
        
        puan_tablosu.append({"Takım": t, "O": O, "G": G, "B": B, "M": M, "AV": int(AV), "P": P})
        
    df_puan = pd.DataFrame(puan_tablosu)
    df_puan = df_puan.sort_values(by=['P', 'AV'], ascending=False).reset_index(drop=True)
    df_puan.index += 1 # Sıralama 1'den başlasın
    return df_puan

# --- ANALİZ MOTORU ---
def mantikli_analiz(ev, dep, df):
    ev_stats = df[df['HomeTeam'] == ev]
    dep_stats = df[df['AwayTeam'] == dep]
    if len(ev_stats) < 2 or len(dep_stats) < 2: return None

    # Beklentiler
    ev_beklenti = (ev_stats['FTHG'].mean() + dep_stats['FTAG'].mean()) / 2
    dep_beklenti = (dep_stats['FTAG'].mean() + ev_stats['FTHG'].mean()) / 2
    
    # Mantık Zinciri
    toplam_gol = ev_beklenti + dep_beklenti
    
    # Skor
    skor_ev = int(round(ev_beklenti))
    skor_dep = int(round(dep_beklenti))
    
    # KG VAR Mantığı: İki tarafın da gol atma ihtimali yüksekse
    kg = "VAR" if (ev_beklenti > 0.8 and dep_beklenti > 0.8) else "YOK"
    
    # 2.5 Alt/Üst Mantığı: Toplam gol 2.4'ü geçiyorsa ÜST
    alt_ust = "2.5 ÜST" if toplam_gol >= 2.4 else "2.5 ALT"
    
    # Maç Sonucu Mantığı
    fark = ev_beklenti - dep_beklenti
    if fark > 0.3: ms = f"MS 1 ({ev})"
    elif fark < -0.3: ms = f"MS 2 ({dep})"
    else: ms = "MS 0 (Beraberlik)"
    
    # İbre
    ibre = 50 + (fark * 20)
    ibre = max(10, min(90, ibre))

    return {
        "skor": f"{skor_ev} - {skor_dep}", "kg": kg, "alt_ust": alt_ust, "ms": ms, "ibre": ibre,
        "ev_xG": ev_beklenti, "dep_xG": dep_beklenti
    }

# --- ARAYÜZ ---
st.title("🦁 FUTBOL KAHİNİ MERKEZİ")

# --- SEKMELER (NAVIGASYON) ---
tab_analiz, tab_puan, tab_live, tab_chat = st.tabs(["🕵️‍♂️ DETAYLI ANALİZ", "🏆 PUAN DURUMU", "📺 CANLI SKOR", "🤖 ASİSTAN"])

# ================= SEKME 1: ANALİZ =================
with tab_analiz:
    st.markdown("### MAÇ ANALİZ ROBOTU")
    
    c1, c2, c3 = st.columns([2,2,2])
    with c1: secilen_lig = st.selectbox("LİG SEÇ", list(lig_kodlari.keys()))
    
    df = veri_yukle(secilen_lig)
    
    if df is not None:
        takimlar = sorted(df['HomeTeam'].unique())
        with c2: ev = st.selectbox("EV SAHİBİ", takimlar)
        with c3: dep = st.selectbox("DEPLASMAN", takimlar, index=1)
        
        if st.button("ANALİZİ BAŞLAT 🚀"):
            res = mantikli_analiz(ev, dep, df)
            
            if res:
                st.divider()
                # 1. BÜYÜK SKOR KARTI
                st.markdown(f"""
                <div class="stat-card" style="border-left: 5px solid #00E676;">
                    <div class="card-title">YAPAY ZEKA TAHMİNİ</div>
                    <div class="big-score">{res['skor']}</div>
                    <div style="font-size: 18px; color: white;">{res['ms']}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # 2. DETAYLAR
                col_d1, col_d2, col_d3 = st.columns(3)
                with col_d1:
                    st.markdown(f"""<div class="stat-card"><div class="card-title">2.5 GOL BARAJI</div><div style="font-size:20px; font-weight:bold; color:white;">{res['alt_ust']}</div></div>""", unsafe_allow_html=True)
                with col_d2:
                    st.markdown(f"""<div class="stat-card"><div class="card-title">KG (KARŞILIKLI GOL)</div><div style="font-size:20px; font-weight:bold; color:white;">{res['kg']}</div></div>""", unsafe_allow_html=True)
                with col_d3:
                    st.markdown(f"""<div class="stat-card"><div class="card-title">KAZANMA İBRESİ</div><div style="font-size:20px; font-weight:bold; color:white;">%{res['ibre']:.0f}</div></div>""", unsafe_allow_html=True)

                # 3. GRAFİK
                fig = go.Figure(go.Indicator(
                    mode = "gauge+number", value = res['ibre'],
                    title = {'text': "Kazanma Şansı"},
                    gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': "white"}, 'steps': [{'range': [0, 45], 'color': "#FF5252"}, {'range': [55, 100], 'color': "#00E676"}]}
                ))
                fig.update_layout(height=200, margin=dict(t=30,b=20,l=20,r=20), paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"})
                st.plotly_chart(fig, use_container_width=True)

# ================= SEKME 2: PUAN DURUMU (YENİ!) =================
with tab_puan:
    st.markdown(f"### 🏆 {secilen_lig} PUAN DURUMU")
    if df is not None:
        puan_df = puan_durumu_hesapla(df)
        st.dataframe(puan_df, use_container_width=True)
    else:
        st.error("Veri yüklenemedi.")

# ================= SEKME 3: CANLI SKOR =================
with tab_live:
    st.markdown("### 📺 CANLI MAÇ MERKEZİ")
    components.html("""<iframe src="https://www.livescore.bz" width="100%" height="600" frameborder="0" style="background-color: #eee; border-radius: 8px;"></iframe>""", height=600, scrolling=True)

# ================= SEKME 4: SOHBET =================
with tab_chat:
    st.markdown("### 🤖 ASİSTAN JARVIS")
    if "messages" not in st.session_state: st.session_state.messages = [{"role": "assistant", "content": "Selam! Futbol veya genel kültür, ne istersen sor."}]
    
    for msg in st.session_state.messages: st.chat_message(msg["role"]).write(msg["content"])
    
    if prompt := st.chat_input("Mesaj yaz..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        
        # Basit Sohbet Cevapları
        cevap = "Bunu tam anlamadım."
        p = prompt.lower()
        if "naber" in p: cevap = "İyiyim! Ligleri analiz ediyorum."
        elif "başkent" in p and "türkiye" in p: cevap = "Ankara."
        elif "fener" in p or "galatasaray" in p: cevap = "Analiz sekmesine gidip maçı seçersen sana detaylı rapor verebilirim."
        
        st.chat_message("assistant").write(cevap)
        st.session_state.messages.append({"role": "assistant", "content": cevap})
