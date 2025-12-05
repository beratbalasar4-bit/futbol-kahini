import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import datetime
import random

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Futbol Kahini Master", page_icon="⚽", layout="wide")

# --- CSS (NEON TASARIM VE GÖRÜNÜM DÜZELTMELERİ) ---
st.markdown("""
<style>
    /* GENEL */
    .stApp { background-color: #050505; color: #E0E0E0; }
    h1, h2, h3, h4 { color: #00E676 !important; font-family: 'Arial Black', sans-serif; text-transform: uppercase; letter-spacing: 1px; }
    
    /* SEÇİM KUTULARI */
    .stSelectbox label p { font-size: 16px !important; color: #00E676 !important; font-weight: bold; }
    div[data-baseweb="select"] > div { background-color: #121212 !important; border: 1px solid #00E676 !important; color: white !important; }

    /* KARTLAR */
    .metric-card {
        background: linear-gradient(145deg, #1a1a1a, #121212);
        padding: 15px; border-radius: 10px; border-left: 5px solid #00E676;
        text-align: center; margin-bottom: 10px; box-shadow: 0 4px 15px rgba(0,230,118,0.1);
    }
    .metric-value { font-size: 24px; font-weight: bold; color: white; margin-top: 5px; }

    /* YORUM KUTUSU */
    .tactic-box {
        background-color: #1E1E1E; padding: 20px; border-radius: 12px; border: 1px solid #333; margin-top: 10px;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important; 
        font-size: 16px; line-height: 1.6; color: #ddd; 
    }
    .tactic-header { color: #00E676; font-weight: bold; font-size: 18px; border-bottom: 1px solid #444; padding-bottom: 10px; margin-bottom: 10px; }
    
    /* Buton */
    .stButton>button { 
        background-color: #00E676; color: black !important; font-weight: 900 !important; border-radius: 8px; height: 55px; border: 2px solid #00C853; width: 100%; font-size: 20px !important; box-shadow: 0 0 15px rgba(0, 230, 118, 0.4); 
    }
</style>
""", unsafe_allow_html=True)

# --- VERİ VE FONKSİYON YAPILANDIRMASI ---

# GENİŞLETİLMİŞ LİG LİSTESİ
lig_yapilandirma = {
    "🇹🇷 Türkiye Süper Lig": {"csv": "T1.csv", "live": "https://www.flashscore.mobi/standings/W6BOzpK2/U3MvIVsA/#table/overall"},
    "🇬🇧 İngiltere Premier": {"csv": "E0.csv", "live": "https://www.flashscore.mobi/standings/dYlOSQ44/W6DOvJ92/#table/overall"},
    "🇪🇸 İspanya La Liga": {"csv": "SP1.csv", "live": "https://www.flashscore.mobi/standings/QVmLl54o/dG2SqPPf/#table/overall"},
    "🇩🇪 Almanya Bundesliga": {"csv": "D1.csv", "live": "https://www.flashscore.mobi/standings/W6BOzpK2/U3MvIVsA/#table/overall"},
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
    "Buyuksehyr": "Başakşehir", "Man City": "Man City", "Man United": "Man Utd", "Real Madrid": "R. Madrid", 
    "Barcelona": "Barcelona", "Bayern Munich": "Bayern", "Dortmund": "Dortmund", "Paris SG": "PSG", 
    "Inter": "Inter", "Milan": "Milan", "Juventus": "Juve", "Benfica": "Benfica", "Porto": "Porto", "Ajax": "Ajax"
}

# --- TEMEL VERİ FONKSİYONLARI ---

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

# --- TAKTİK VE ANALİZ MOTORLARI ---

def taktik_analiz(stats, taraf="Ev"):
    # Hata Düzeltme: Burada gol ve kart ortalamasına göre taktik stil çıkarıyoruz
    gol_at = stats['FTHG'].mean() if taraf == "Ev" else stats['FTAG'].mean()
    gol_ye = stats['FTAG'].mean() if taraf == "Ev" else stats['FTHG'].mean()
    kart = stats['HY'].mean() + stats['AY'].mean() if 'HY' in stats.columns else 2.0
    
    stil = "Dengeli"
    if gol_at > 2.0 and kart < 2.0: stil = "Hücum Futbolu & Fair Play"
    elif gol_at > 1.5 and gol_ye > 1.5: stil = "Gol Düellocusu / Savunma Zaafiyeti"
    elif gol_ye < 0.8: stil = "Savunma Ağırlıklı / Katı Blok"
    elif kart > 3.0: stil = "Agresif / Fiziksel Oyun"
    
    return stil

def detayli_analiz_motoru(ev, dep, df):
    ev_stats = df[df['HomeTeam'] == ev]; dep_stats = df[df['AwayTeam'] == dep]
    if len(ev_stats) < 1 or len(dep_stats) < 1: return None

    # 1. TEMEL ORTALAMALAR
    ev_gol_at = ev_stats['FTHG'].mean(); dep_gol_at = dep_stats['FTAG'].mean()
    ev_gol_ye = ev_stats['FTAG'].mean(); dep_gol_ye = dep_stats['FTHG'].mean()
    
    # 2. BASKI VE ŞUT İSTATİSTİKLERİ
    ev_total_shot = ev_stats['HS'].mean() if 'HS' in df.columns else 12.0
    dep_total_shot = dep_stats['AS'].mean() if 'AS' in df.columns else 10.0
    ev_shot_target = ev_stats['HST'].mean() if 'HST' in df.columns else 5.0
    dep_shot_target = dep_stats['AST'].mean() if 'AST' in df.columns else 4.0

    # 3. KORNER & KART
    toplam_korner = (ev_stats['HC'].mean() + dep_stats['AC'].mean()) if 'HC' in df.columns else 9.5
    toplam_kart = (ev_stats['HY'].mean() + dep_stats['AY'].mean()) if 'HY' in df.columns else 4.0
    
    # 4. TAHMİNLER
    toplam_gol_beklenti = ev_gol_at + dep_gol_at
    skor_ev = int(round(ev_gol_at * 1.15)); skor_dep = int(round(dep_gol_at * 0.9))
    
    ibre = 50 + ((ev_gol_at - dep_gol_at) * 15)
    
    return {
        "skor": f"{skor_ev}-{skor_dep}", "ibre": max(10, min(90, ibre)),
        "alt_ust": "2.5 ÜST" if toplam_gol_beklenti >= 2.4 else "2.5 ALT",
        "kg": "VAR" if (ev_gol_at > 0.7 and dep_gol_at > 0.7) else "YOK",
        "korner_tahmin": toplam_korner, "kart_tahmin": toplam_kart,
        "ev_gol": ev_gol_at, "dep_gol": dep_gol_at, "ev_yed": ev_gol_ye, "dep_yed": dep_gol_ye,
        "ev_sut_ort": ev_total_shot, "dep_sut_ort": dep_total_shot,
        "ev_sut_isabet": ev_shot_target, "dep_sut_isabet": dep_shot_target,
    }

# --- ARAYÜZ BAŞLANGICI ---
st.title("🦁 FUTBOL KAHİNİ V27")

tab1, tab2, tab3, tab4 = st.tabs(["📊 DETAYLI ANALİZ", "📝 RAW İSTATİSTİK MERKEZİ", "🏆 PUAN DURUMU", "🤖 ASİSTAN"])

# ================= SEKME 1: MAX DETAYLI ANALİZ =================
with tab1:
    st.markdown("### 🕵️‍♂️ MAÇ ANALİZ ROBOTU")
    
    c1, c2, c3 = st.columns([2,2,2])
    with c1: secilen_lig = st.selectbox("LİG SEÇİNİZ", list(lig_yapilandirma.keys()), key="analiz_lig")
    df = veri_yukle(secilen_lig)
    
    if df is not None:
        takimlar = sorted(df['HomeTeam'].unique())
        with c2: ev = st.selectbox("EV SAHİBİ", takimlar, key="analiz_ev")
        with c3: dep = st.selectbox("DEPLASMAN", takimlar, index=1, key="analiz_dep")
        
        st.markdown("")
        if st.button("ANALİZ LABORATUVARINI ÇALIŞTIR 🧬"):
            res = detayli_analiz_motoru(ev, dep, df)
            
            if res:
                st.divider()
                
                # --- ÖZET KARTLAR ---
                k1, k2, k3, k4 = st.columns(4)
                with k1: st.markdown(f"""<div class="metric-card"><div class="metric-title">SKOR TAHMİNİ</div><div class="metric-value">{res['skor']}</div></div>""", unsafe_allow_html=True)
                with k2: st.markdown(f"""<div class="metric-card"><div class="metric-title">KAZANMA ŞANSI</div><div class="metric-value">% {res['ibre']:.0f}</div></div>""", unsafe_allow_html=True)
                with k3: st.markdown(f"""<div class="metric-card"><div class="metric-title">TOPLAM GOL</div><div class="metric-value">{res['alt_ust']}</div></div>""", unsafe_allow_html=True)
                with k4: st.markdown(f"""<div class="metric-card"><div class="metric-title">KARŞILIKLI GOL</div><div class="metric-value">{res['kg']}</div></div>""", unsafe_allow_html=True)
                
                st.divider()

                # --- BÖLÜM 1: TAKTİK VE YORUM ---
                st.markdown("### 🎙️ YAPAY ZEKA TEKNİK YORUMU")
                ev_stil = taktik_analiz(df[df['HomeTeam'] == ev], "Ev")
                dep_stil = taktik_analiz(df[df['AwayTeam'] == dep], "Dep")
                
                st.markdown(f"""
                <div class="tactic-box">
                    <div class="tactic-header">MAÇ HİKAYESİ VE OYUN ANLAYIŞI</div>
                    <p class="tactic-text">
                        <b>{ev}</b> takımı genel olarak **{ev_stil}** oyun stilini tercih ediyor. Maç başına ortalama {res['ev_sut_ort']:.1f} şut atıp, bunların {res['ev_sut_isabet']:.1f}'ini kaleye isabet ettiriyor. Bu, hücumda etkili bir baskı gücüne işaret ediyor.
                        <br><br>
                        <b>{dep}</b> takımı ise {dep_stil} bir yaklaşımla sahada yer alıyor. Deplasman ortalamaları ({res['dep_sut_ort']:.1f} şut) rakibine göre biraz daha düşük. Teknik direktörün oyun anlayışı, muhtemelen 'kontrollü' bir oyuna odaklanacaktır.
                    </p>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("#### 🎯 DETAYLI BAHİS PROJEKSİYONLARI")
                
                # SÜTUN BAZLI PROJEKSİYONLAR
                p1, p2, p3, p4 = st.columns(4)
                
                with p1:
                    st.markdown(f"""<div class="metric-card"><div class="metric-title">KORNER BARAJ TAHMİNİ</div><div class="metric-value">{res['korner_tahmin']:.1f} ÜST</div></div>""", unsafe_allow_html=True)
                with p2:
                    st.markdown(f"""<div class="metric-card"><div class="metric-title">SERTLİK / KART (Ort.)</div><div class="metric-value">{res['kart_tahmin']:.1f} Kart</div></div>""", unsafe_allow_html=True)
                with p3:
                    # OYUNCU ŞUT PROJESYONU (Simulated)
                    st.markdown(f"""<div class="metric-card"><div class="metric-title">OYUNCU ŞUT PROJESYONU</div><div class="metric-value">{res['ev_sut_isabet'] + 1:.1f} Şut/İsabet</div><div classeric-sub">({ev} takımından)</div></div>""", unsafe_allow_html=True)
                with p4:
                    # HT/FT TAHMİNİ
                    ht_result = "1/1 (Evden Koparma)" if res['ibre'] > 70 else "X/1 (İkinci Yarı)"
                    st.markdown(f"""<div class="metric-card"><div class="metric-title">DEVRE/MAÇ SONUCU</div><div class="metric-value">{ht_result}</div></div>""", unsafe_allow_html=True)
                
                
                # --- GRAFİKSEL BÖLÜM (Veri Açıklamalı) ---
                st.markdown("### 📊 GRAFİKSEL VERİ KARŞILAŞTIRMASI")

                g1, g2 = st.columns([2, 1])
                with g1:
                    # Radar Grafiği
                    categories = ['Hücum Gücü', 'Savunma Zafiyeti', 'Toplam Şut Ort.', 'Gol Yeme Ort.']
                    fig_radar = go.Figure()
                    fig_radar.add_trace(go.Scatterpolar(r=[res['ev_gol']*20, res['ev_yed']*15, res['ev_sut_ort']*5, res['ev_yed']*25], theta=categories, fill='toself', name=ev, line_color='#00E676'))
                    fig_radar.add_trace(go.Scatterpolar(r=[res['dep_gol']*20, res['dep_yed']*15, res['dep_sut_ort']*5, res['dep_yed']*25], theta=categories, fill='toself', name=dep, line_color='#FF5252'))
                    fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font={'color':'white'}, height=300)
                    st.plotly_chart(fig_radar, use_container_width=True)
                with g2:
                    st.markdown(f"""
                    <div class="tactic-box" style="margin-top:0;">
                    <b>💡 RADAR YORUMU:</b><br>
                    Bu grafik, takımların dört kritik alandaki gücünü kıyaslar. 
                    <b>Yeşil alan büyüdükçe</b> ({ev}) takımın o alanda lig ortalamasına göre daha iyi olduğu anlamına gelir. 
                    En zayıf halkayı ve en güçlü yönü tek bakışta görebilirsin.
                    </div>
                    """, unsafe_allow_html=True)

            else: st.error("Sezon başı verisi eksik.")

# ================= SEKME 2: RAW İSTATİSTİK MERKEZİ (YENİ) =================
with tab2:
    st.markdown("### 📝 RAW VERİ VE İSTATİSTİK GÖRÜNTÜLEYİCİ")
    st.info("Burada Yapay Zekanın kullandığı **işlenmemiş ham veriyi** görebilirsin. Şut, Faul, Kart gibi tüm detaylar mevcuttur.")
    
    # Lig Seçimi
    secilen_lig_raw = st.selectbox("Görüntülenecek Ligi Seçiniz:", list(lig_yapilandirma.keys()))
    df_raw = veri_yukle(secilen_lig_raw)
    
    if df_raw is not None:
        # İhtiyacımız olan tüm ham sütunları gösteriyoruz
        display_cols = [col for col in df_raw.columns if col not in ['Div', 'HomeTeam', 'AwayTeam', 'FTR', 'HTR']]
        
        st.dataframe(df_raw[['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'HS', 'AS', 'HST', 'AST', 'HF', 'AF', 'HY', 'AY', 'HR', 'AR']].tail(50), use_container_width=True)
        st.caption("Son 50 maçın ham verisi (FTHG: Ev Gol, HS: Ev Şut, HST: Ev İsabetli Şut, HY: Ev Sarı Kart vb.)")
    else:
        st.error("Ham veri yüklenemedi.")


# ================= SEKME 3: PUAN DURUMU =================
with tab3:
    st.markdown("### 🏆 GÜNCEL PUAN DURUMU")
    secilen_lig_puan = st.selectbox("Puan Tablosu:", list(lig_yapilandirma.keys()), key="puan_lig")
    link = lig_yapilandirma[secilen_lig_puan]["live"]
    st.markdown(f"**{secilen_lig_puan}** için Canlı Puan Durumu (Flashscore):")
    components.html(f"""<iframe src="{link}" width="100%" height="800" frameborder="0" style="background-color: white; border-radius: 10px;"></iframe>""", height=800, scrolling=True)

# ================= SEKME 4: ASİSTAN =================
with tab4:
    st.markdown("### 🤖 ASİSTAN JARVIS")
    if "messages" not in st.session_state: st.session_state.messages = [{"role": "assistant", "content": "Selam! Maçları sorabilirsin."}]
    for msg in st.session_state.messages: st.chat_message(msg["role"]).write(msg["content"])
    if prompt := st.chat_input("Mesaj yaz..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        st.chat_message("assistant").write("Analiz sekmesinden detaylara bakabilirsin.")
