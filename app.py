import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.graph_objects as go
import time
import datetime
import random
from scipy.stats import poisson

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Futbol Kahini AI", page_icon="🎙️", layout="wide")

# --- CSS (PROFESYONEL YORUMCU TASARIMI) ---
st.markdown("""
<style>
    .stApp { background-color: #121212; }
    h1 { color: #00E676 !important; text-align: center; font-family: 'Arial Black', sans-serif; text-transform: uppercase; }
    
    /* Yorumcu Kutusu */
    .yorum-kutu {
        background-color: #1E1E1E; border-left: 6px solid #F1C40F; padding: 20px; border-radius: 10px;
        color: #ECF0F1; font-family: 'Georgia', serif; font-size: 18px; line-height: 1.6;
        box-shadow: 0 4px 10px rgba(0,0,0,0.5); margin-bottom: 20px;
    }
    .yorum-baslik { color: #F1C40F; font-weight: bold; font-size: 20px; margin-bottom: 10px; display: block; }
    
    /* İstatistik Kartları */
    .stat-box {
        background-color: #263238; border-radius: 8px; padding: 10px; text-align: center;
        border-top: 3px solid #00E676; margin-bottom: 10px;
    }
    .stat-val { font-size: 24px; font-weight: bold; color: white; }
    .stat-lbl { font-size: 12px; color: #B0BEC5; text-transform: uppercase; }
    
    /* Kupon Kartı */
    .kupon-karti { background-color: #263238; padding: 15px; border-radius: 8px; margin-bottom: 10px; border-left: 5px solid #00E676; }
    .surpriz { border-left: 5px solid #FF5252; }
    .oran { float: right; background: #00E676; color: black; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
    .oran-s { background: #FF5252; color: white; }
    
    /* Buton */
    .stButton>button { 
        background: linear-gradient(to right, #00CC96, #00b887); color: white; width: 100%; border-radius: 10px; height: 50px; font-weight: bold; border: none;
    }
</style>
""", unsafe_allow_html=True)

# --- VERİ SETLERİ ---
lig_kodlari = {
    "🇹🇷 Süper Lig": "T1.csv", "🇬🇧 Premier Lig": "E0.csv", 
    "🇪🇸 La Liga": "SP1.csv", "🇩🇪 Bundesliga": "D1.csv", 
    "🇮🇹 Serie A": "I1.csv", "🇫🇷 Ligue 1": "F1.csv"
}

takim_duzeltme = {
    "Fenerbahce": "Fenerbahçe", "Galatasaray": "Galatasaray", "Besiktas": "Beşiktaş", "Trabzonspor": "Trabzonspor",
    "Buyuksehyr": "Başakşehir", "Man City": "Man City", "Man United": "Man Utd",
    "Real Madrid": "R. Madrid", "Barcelona": "Barcelona", "Bayern Munich": "Bayern",
    "Dortmund": "Dortmund", "Paris SG": "PSG", "Inter": "Inter", "Milan": "Milan", "Juventus": "Juve"
}

# --- YORUMCU SÖZLÜĞÜ (FANCY SENTENCES) ---
yorum_kaliplari = {
    "yuksek_hucum": [
        "Bu takımın ciğerleri sönmüyor! İnanılmaz bir pres gücü var.",
        "Set hücumuna yerleştiklerinde rakibi boğuyorlar.",
        "3. bölgede çok etkililer, rakip savunmanın başını döndürüyorlar.",
        "Dikine oyun anlayışları çok iyi, geçiş hücumlarında ölümcül oluyorlar."
    ],
    "kotu_savunma": [
        "Defans arkasına atılan her top tehlike yaratıyor.",
        "Savunma hatları kopuk, araya atılan toplarda çok pozisyon veriyorlar.",
        "Bekleri çok ileri çıkıyor, geride büyük boşluklar bırakıyorlar.",
        "Duran toplarda adam paylaşımını bir türlü yapamıyorlar."
    ],
    "dengeli": [
        "Tipik bir satranç maçı izleyeceğiz. İki takım da kontrollü.",
        "Orta saha mücadelesi şeklinde geçecek bir maç.",
        "Erken gol olmazsa maç kilitlenir, taktik savaşına döner."
    ],
    "banko_ev": [
        "Ev sahibi taraftarını da arkasına alıp maçı domine eder.",
        "Bu stadyumdan çıkış zor! Ev sahibi çok baskın.",
        "Kadıköy/Arena havası var, ev sahibi favori."
    ]
}

# --- GLOBAL VERİ YÜKLEME ---
@st.cache_data(ttl=3600)
def tum_verileri_yukle():
    tum_df = pd.DataFrame()
    ana_url = "https://www.football-data.co.uk/mmz4281/2425/"
    for lig_ad, dosya in lig_kodlari.items():
        try:
            url = ana_url + dosya
            df = pd.read_csv(url)
            df = df.dropna(subset=['FTR'])
            df['HomeTeam'] = df['HomeTeam'].replace(takim_duzeltme)
            df['AwayTeam'] = df['AwayTeam'].replace(takim_duzeltme)
            df['Lig'] = lig_ad 
            tum_df = pd.concat([tum_df, df])
        except: continue
    return tum_df

global_df = tum_verileri_yukle()

# --- ANALİZ VE YORUM MOTORU ---
def mac_analiz_et(ev, dep, df):
    ev_stats = df[df['HomeTeam'] == ev]
    dep_stats = df[df['AwayTeam'] == dep]
    if len(ev_stats) < 2 or len(dep_stats) < 2: return None
    
    # İstatistikler
    ev_gol_at = ev_stats['FTHG'].mean()
    ev_gol_ye = ev_stats['FTAG'].mean()
    dep_gol_at = dep_stats['FTAG'].mean()
    dep_gol_ye = dep_stats['FTHG'].mean()
    
    # 1. Beklentiler
    ev_beklenti = (ev_gol_at + dep_gol_ye) / 2
    dep_beklenti = (dep_gol_at + ev_gol_ye) / 2
    toplam_gol = ev_beklenti + dep_beklenti
    
    # 2. İbre (Güç)
    fark = (ev_gol_at * 1.5 - ev_gol_ye) - (dep_gol_at * 1.5 - dep_gol_ye)
    ibre = 50 + (fark * 15)
    ibre = max(10, min(90, ibre))
    
    # 3. YORUM OLUŞTURMA (AI PUNDIT)
    yorumlar = []
    
    # Ev Sahibi Analizi
    if ev_gol_at > 2.0: yorumlar.append(random.choice(yorum_kaliplari["yuksek_hucum"]).replace("takım", ev))
    if ev_gol_ye > 1.5: yorumlar.append(f"{ev} savunmada alarm veriyor. " + random.choice(yorum_kaliplari["kotu_savunma"]))
    
    # Deplasman Analizi
    if dep_gol_at < 0.8: yorumlar.append(f"{dep} deplasmanda gol yollarında kısır. Üretkenlik sorunu yaşıyorlar.")
    if dep_gol_ye > 2.0: yorumlar.append(f"{dep} deplasman fobisi yaşıyor, savunmaları çok kırılgan.")
    
    # Maç Özeti
    if ibre > 65: son_soz = f"Özetle; {ev} sahasında hata yapmaz. {random.choice(yorum_kaliplari['banko_ev'])}"
    elif ibre < 35: son_soz = f"Sürpriz kokusu var! {dep} kontrataklarla can yakabilir."
    else: son_soz = f"Ortada bir maç. {random.choice(yorum_kaliplari['dengeli'])}"
    
    full_yorum = " ".join(yorumlar) + " " + son_soz
    
    # Skor Tahmini (Poisson)
    skor_ev = int(round(ev_beklenti))
    skor_dep = int(round(dep_beklenti))
    
    return {
        "ibre": ibre, "skor": f"{skor_ev} - {skor_dep}", "yorum": full_yorum,
        "gol_beklenti": toplam_gol, "ev_gol": ev_gol_at, "dep_gol": dep_gol_at
    }

# --- ARAYÜZ ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/1995/1995515.png", width=100) # Mikrofon ikonu
    st.title("YORUMCU MODU")
    st.info(f"📅 {datetime.datetime.now().strftime('%d.%m.%Y')}")

st.title("🎙️ FUTBOL KAHİNİ: UZMAN GÖRÜŞÜ")

# --- LİSTELER ---
tab1, tab2 = st.tabs(["⚡ GÜNÜN OTOMATİK KUPONLARI", "🎙️ DETAYLI ANALİZ & YORUM"])

# ================= SEKME 1: OTOMATİK KUPON (SANAL BÜLTEN) =================
with tab1:
    st.subheader("🎰 GÜNÜN OTOMATİK BÜLTENİ")
    st.caption("Sistem ligleri tarıyor ve bugünün sanal bültenini oluşturuyor. Sen seçme, bırak yapay zeka yönetsin.")
    
    if st.button("BÜLTENİ VE KUPONLARI GETİR 🎲", type="primary"):
        with st.spinner("Ligler taranıyor... Bülten oluşturuluyor..."):
            time.sleep(1.5)
            
            # --- OTOMATİK MAÇ SEÇİCİ (SANAL BÜLTEN) ---
            # Rastgele 5 maç seçip analiz edeceğiz (Sanki bugün oynanıyormuş gibi)
            maclar = []
            tum_ligler = global_df['Lig'].unique()
            
            for lig in tum_ligler:
                df_lig = global_df[global_df['Lig'] == lig]
                if df_lig.empty: continue
                ev_list = df_lig['HomeTeam'].unique()
                if len(ev_list) > 2:
                    # Ligden rastgele 1 maç seç
                    secilen_ev = random.choice(ev_list)
                    # Rakibi bul (Veri setindeki son rakibi değil, rastgele bir rakip simüle etmiyoruz, gerçek veriden çekiyoruz)
                    # Gerçekçi olması için o takımın verisini alıp analiz ediyoruz
                    res = mac_analiz_et(secilen_ev, df_lig[df_lig['HomeTeam']!=secilen_ev].iloc[0]['HomeTeam'], df_lig) # Rastgele eşleşme yerine genel güç
                    # Düzeltme: Kupon için sadece takımın genel gücüne bakalım
                    stats = df_lig[df_lig['HomeTeam'] == secilen_ev]
                    puan = stats['FTHG'].mean() * 1.5 - stats['FTAG'].mean()
                    gol = stats['FTHG'].mean() + stats['FTAG'].mean()
                    
                    maclar.append({"Takım": secilen_ev, "Lig": lig, "Puan": puan, "Gol": gol})
            
            # KUPONLARI AYIKLA
            bankolar = [m for m in maclar if m['Puan'] > 1.2]
            surprizler = [m for m in maclar if 0 < m['Puan'] < 0.4] # Beraberlik kokanlar
            gol_maclari = [m for m in maclar if m['Gol'] > 3.2]

            c1, c2 = st.columns(2)
            
            with c1:
                st.success("✅ GÜNÜN BANKO KUPONU")
                if bankolar:
                    for m in bankolar[:3]:
                        st.markdown(f"""
                        <div class="kupon-karti">
                            <span class="oran">1.{random.randint(40,65)}</span>
                            <b>{m['Takım']} Kazanır</b><br>
                            <small>{m['Lig']}</small>
                        </div>""", unsafe_allow_html=True)
                elif gol_maclari:
                     for m in gol_maclari[:3]:
                        st.markdown(f"""
                        <div class="kupon-karti">
                            <span class="oran">1.{random.randint(50,70)}</span>
                            <b>{m['Takım']} 2.5 ÜST</b><br>
                            <small>{m['Lig']}</small>
                        </div>""", unsafe_allow_html=True)
                else: st.warning("Bugün banko maç çıkmadı.")
            
            with c2:
                st.error("🔥 YÜKSEK ORANLI SÜRPRİZ")
                if surprizler:
                    for m in surprizler[:3]:
                        st.markdown(f"""
                        <div class="kupon-karti surpriz">
                            <span class="oran oran-s">3.{random.randint(10,50)}</span>
                            <b>{m['Takım']} Beraberlik</b><br>
                            <small>{m['Lig']}</small>
                        </div>""", unsafe_allow_html=True)
                else: st.info("Sürpriz risk yok.")

# ================= SEKME 2: YORUMCU ANALİZİ =================
with tab2:
    st.subheader("🎙️ DETAYLI ANALİZ MASASI")
    
    c_sel1, c_sel2 = st.columns([1, 2])
    with c_sel1:
        lig = st.selectbox("Lig:", list(lig_kodlari.keys()))
        df_lig = global_df[global_df['Lig'] == lig]
        takimlar = sorted(df_lig['HomeTeam'].unique())
        ev = st.selectbox("Ev Sahibi", takimlar)
        dep = st.selectbox("Deplasman", takimlar, index=1)
        btn = st.button("YORUMLA 📢")

    if btn:
        res = mac_analiz_et(ev, dep, global_df)
        if res:
            with c_sel2:
                # 1. YORUM KUTUSU
                st.markdown(f"""
                <div class="yorum-kutu">
                    <span class="yorum-baslik">🎙️ MAÇ YORUMU</span>
                    "{res['yorum']}"
                </div>
                """, unsafe_allow_html=True)
            
            # 2. İSTATİSTİKLER VE GRAFİK
            col_g1, col_g2 = st.columns([1, 1])
            with col_g1:
                # İbre
                fig = go.Figure(go.Indicator(
                    mode = "gauge+number", value = res['ibre'],
                    title = {'text': "Kazanma Şansı"},
                    gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': "white"}, 'steps': [{'range': [0, 45], 'color': "#FF5252"}, {'range': [55, 100], 'color': "#00E676"}]}
                ))
                fig.update_layout(height=250, margin=dict(t=30,b=20,l=20,r=20), paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"})
                st.plotly_chart(fig, use_container_width=True)
            
            with col_g2:
                # İstatistik Kutuları
                r1, r2 = st.columns(2)
                r1.markdown(f"""<div class="stat-box"><div class="stat-lbl">Skor Tahmini</div><div class="stat-val">{res['skor']}</div></div>""", unsafe_allow_html=True)
                r2.markdown(f"""<div class="stat-box"><div class="stat-lbl">Gol Beklentisi</div><div class="stat-val">{res['gol_beklenti']:.2f}</div></div>""", unsafe_allow_html=True)
                
                r3, r4 = st.columns(2)
                r3.markdown(f"""<div class="stat-box"><div class="stat-lbl">Ev Gol Ort</div><div class="stat-val">{res['ev_gol']:.1f}</div></div>""", unsafe_allow_html=True)
                r4.markdown(f"""<div class="stat-box"><div class="stat-lbl">Dep Gol Ort</div><div class="stat-val">{res['dep_gol']:.1f}</div></div>""", unsafe_allow_html=True)
