import streamlit as st
import streamlit.components.v1 as components 
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import datetime
import random
import numpy as np # NaN kontrolü için

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Futbol Kahini Master", page_icon="⚽", layout="wide")

# --- CSS (NEON TASARIM) ---
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

def get_safe_mean(df_slice, col_name, default=0.0):
    if col_name in df_slice.columns:
        mean_val = df_slice[col_name].mean()
        # HATA DÜZELTME: NaN yerine güvenli 0.0 döndürüyoruz
        return mean_val if pd.notna(mean_val) else default
    return default

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

# --- RAW DATA HESAPLAMA ---
def raw_data_hesapla(df):
    teams = df['HomeTeam'].unique()
    raw_stats = []
    
    for team in teams:
        home = df[df['HomeTeam'] == team]
        away = df[df['AwayTeam'] == team]
        O = len(home) + len(away)
        
        avg_data = {
            "Takım": team,
            "Oynanan Maç": O,
            "Gol Ort.": (home['FTHG'].sum() + away['FTAG'].sum()) / O,
            "Yediği Gol Ort.": (home['FTAG'].sum() + away['FTHG'].sum()) / O,
        }
        
        if 'HS' in df.columns:
             avg_data["Şut Ort."] = (home['HS'].sum() + away['AS'].sum()) / O
             avg_data["İsabetli Şut Ort."] = (home['HST'].sum() + away['AST'].sum()) / O
        
        if 'HF' in df.columns:
            avg_data["Faul Ort."] = (home['HF'].sum() + away['AF'].sum()) / O
        
        if 'HY' in df.columns:
            avg_data["Sarı Kart Ort."] = (home['HY'].sum() + away['AY'].sum()) / O
            
        raw_stats.append(avg_data)
        
    df_raw = pd.DataFrame(raw_stats).sort_values(by='Gol Ort.', ascending=False).reset_index(drop=True)
    df_raw.index += 1
    return df_raw

# --- TAKTİK VE ANALİZ MOTORLARI ---

def taktik_analiz(stats, taraf="Ev"):
    gol_at = get_safe_mean(stats, 'FTHG' if taraf == "Ev" else 'FTAG')
    gol_ye = get_safe_mean(stats, 'FTAG' if taraf == "Ev" else 'FTHG')
    kart = get_safe_mean(stats, 'HY') + get_safe_mean(stats, 'AY') # Sarı kart
    
    stil = "Dengeli"
    if gol_at > 2.0 and kart < 2.0: stil = "Hücum Futbolu & Fair Play"
    elif gol_at > 1.5 and gol_ye > 1.5: stil = "Gol Düellocusu / Savunma Zaafiyeti"
    elif gol_ye < 0.8: stil = "Savunma Ağırlıklı / Katı Blok"
    elif kart > 3.0: stil = "Agresif / Fiziksel Oyun"
    
    return stil

def detayli_analiz_motoru(ev, dep, df):
    ev_stats = df[df['HomeTeam'] == ev]; dep_stats = df[df['AwayTeam'] == dep]
    if len(ev_stats) < 1 or len(dep_stats) < 1: return None

    # HATA DÜZELTME UYGULANMIŞ İSTATİSTİKLER
    ev_gol_at = get_safe_mean(ev_stats, 'FTHG'); dep_gol_at = get_safe_mean(dep_stats, 'FTAG')
    ev_gol_ye = get_safe_mean(ev_stats, 'FTAG'); dep_gol_ye = get_safe_mean(dep_stats, 'FTHG')
    
    ev_total_shot = get_safe_mean(ev_stats, 'HS', default=12.0); dep_total_shot = get_safe_mean(dep_stats, 'AS', default=10.0)
    ev_shot_target = get_safe_mean(ev_stats, 'HST', default=5.0); dep_shot_target = get_safe_mean(dep_stats, 'AST', default=4.0)

    toplam_korner = get_safe_mean(ev_stats, 'HC', default=5.0) + get_safe_mean(dep_stats, 'AC', default=4.0)
    toplam_kart = get_safe_mean(ev_stats, 'HY') + get_safe_mean(dep_stats, 'AY') # Sadece sarı kartlar
    
    # TAHMİNLER
    toplam_gol_beklenti = ev_gol_at + dep_gol_at
    skor_ev = int(round(ev_gol_at * 1.15)); skor_dep = int(round(dep_gol_at * 0.9))
    
    ibre = 50 + ((ev_gol_at - dep_gol_at) * 15)
    
    # PROJEKSİYONLAR
    return {
        "skor": f"{skor_ev}-{skor_dep}", "ibre": max(10, min(90, ibre)),
        "alt_ust": "2.5 ÜST" if toplam_gol_beklenti >= 2.4 else "2.5 ALT",
        "kg": "VAR" if (ev_gol_at > 0.7 and dep_gol_at > 0.7) else "YOK",
        "korner_tahmin": toplam_korner, "kart_tahmin": toplam_kart,
        "ev_gol": ev_gol_at, "dep_gol": dep_gol_at, "ev_yed": ev_gol_ye, "dep_yed": dep_gol_ye,
        "ev_sut_ort": ev_total_shot, "dep_sut_ort": dep_total_shot,
        "ev_sut_isabet": ev_shot_target, "dep_sut_isabet": dep_shot_target,
        "clean_sheet": "0 GOL YEMEZ" if ev_gol_ye < 0.6 else "GOL YEME RİSKİ YÜKSEK",
        "double_chance": f"1X ({ev} veya Berabere)" if ibre > 45 else f"X2 (Berabere veya {dep})"
    }

# --- ARAYÜZ ---
st.title("🦁 FUTBOL KAHİNİ V29")

tab1, tab2, tabtab3 = st.tabs(["📊 DETAYLI ANALİZ", "📝 RAW İSTATİSTİK MERKEZİ", "🤖 ASİSTAN"]) # PUAN DURUMU KALDIRILDI

# ================= SEKME 1: MAKSİMUM DETAYLI ANALİZ =================
with tab1:
    st.markdown("### 🕵️‍♂️ MAÇ ANALİZ ROBOTU")
    
    # Canlı Form Penceresi hala gerekli, en üste küçük bir expender olarak ekleyelim
    with st.expander("📡 Canlı Form Doğrulama (Tıkla Aç)", expanded=False):
        st.caption("Veriler anlık Flashscore'dan çekilir.")
        link_canli = lig_yapilandirma.get(st.session_state.get('analiz_lig', list(lig_yapilandirma.keys())[0]), {}).get('live', 'https://www.flashscore.mobi')
        components.html(f"""<iframe src="{link_canli}" width="100%" height="300" frameborder="0" style="background:white;"></iframe>""", height=300)

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
                
                # --- BÖLÜM 1: TEKNİK YORUM ---
                st.markdown("### 🎙️ YAPAY ZEKA TEKNİK YORUMU")
                ev_stil = taktik_analiz(df[df['HomeTeam'] == ev], "Ev")
                dep_stil = taktik_analiz(df[df['AwayTeam'] == dep], "Dep")
                
                st.markdown(f"""
                <div class="tactic-box">
                    <div class="tactic-header">MAÇ SENARYOSU</div>
                    <p class="tactic-text">
                        <b>{ev}</b> takımı genel olarak **{ev_stil}** oyun stilini tercih ediyor. Ev sahibi ortalama **{res['ev_sut_ort']:.1f} şut** atıp **{res['ev_sut_isabet']:.1f}** isabet buluyor.
                        <br><br>
                        <b>{dep}</b> takımı ise deplasmanda **{dep_stil}** oynuyor. Teknik direktörün oyun anlayışı **{('Agresif ve Hızlı Geçiş' if res['ibre'] > 60 else 'Kontrollü ve Taktiksel')}** bir mücadeleyi işaret ediyor.
                    </p>
                </div>
                """, unsafe_allow_html=True)

                # --- BÖLÜM 2: PROJEKSİYON VE RAW METRİKLERİ ---
                st.markdown("#### 🎯 EKSTRA BAHİS PROJEKSİYONLARI")
                
                p1, p2, p3, p4 = st.columns(4)
                
                with p1:
                    st.markdown(f"""<div class="metric-card"><div class="metric-title">KORNER BARAJ TAHMİNİ</div><div class="metric-value">{res['korner_tahmin']:.1f} ÜST</div></div>""", unsafe_allow_html=True)
                with p2:
                    st.markdown(f"""<div class="metric-card"><div class="metric-title">GOL YEMEME İHTİMALİ</div><div class="metric-value">{res['clean_sheet']}</div></div>""", unsafe_allow_html=True)
                with p3:
                    # HATA DÜZELTİLDİ
                    st.markdown(f"""<div class="metric-card"><div class="metric-title">OYUNCU ŞUT PROJ.</div><div class="metric-value">{res['ev_sut_isabet'] + 1:.0f} İsabet</div><div style="font-size:11px; color:#aaa;">({ev} yıldızından)</div></div>""", unsafe_allow_html=True)
                with p4:
                    st.markdown(f"""<div class="metric-card"><div class="metric-title">ÇİFTE ŞANS TAHMİNİ</div><div class="metric-value">{res['double_chance']}</div></div>""", unsafe_allow_html=True)
                
                # --- GRAFİKLER (İkinci Kısım) ---
                st.markdown("### 📊 GRAFİKSEL VERİ KARŞILAŞTIRMASI")

                g1, g2 = st.columns([1, 1])
                with g1:
                    # Radar Grafiği
                    categories = ['Hücum Gücü', 'Savunma Zafiyeti', 'Toplam Şut Ort.', 'Gol Yeme Ort.']
                    fig_radar = go.Figure()
                    fig_radar.add_trace(go.Scatterpolar(r=[res['ev_gol']*20, res['ev_yed']*15, res['ev_sut_ort']*5, res['ev_yed']*25], theta=categories, fill='toself', name=ev, line_color='#00E676'))
                    fig_radar.add_trace(go.Scatterpolar(r=[res['dep_gol']*20, res['dep_yed']*15, res['dep_sut_ort']*5, res['dep_yed']*25], theta=categories, fill='toself', name=dep, line_color='#FF5252'))
                    fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font={'color':'white'}, height=300)
                    st.plotly_chart(fig_radar, use_container_width=True)

                with g2:
                    # Baskı Grafiği
                    fig_baski = go.Figure()
                    fig_baski.add_trace(go.Bar(y=['Şut Ort.'], x=[res['ev_sut_ort']], orientation='h', name=ev, marker_color='#00E676'))
                    fig_baski.add_trace(go.Bar(y=['Şut Ort.'], x=[res['dep_sut_ort']], orientation='h', name=dep, marker_color='#FF5252'))
                    fig_baski.update_layout(title="Hücum Yoğunluğu (Şut Ortalaması)", barmode='group', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font={'color':'white'}, height=300)
                    st.plotly_chart(fig_baski, use_container_width=True)


            else: st.error("Veri yetersiz.")

# ================= SEKME 2: RAW İSTATİSTİK MERKEZİ =================
with tab2:
    st.markdown("### 📝 TAKIM ORTALAMA İSTATİSTİKLERİ")
    st.info("Bu tabloda Yapay Zekanın kullandığı **işlenmiş ortalama ham veri** (Maç Başı) yer alır.")
    
    secilen_lig_raw = st.selectbox("Görüntülenecek Ligi Seçiniz:", list(lig_yapilandirma.keys()), key="raw_lig")
    df_raw_base = veri_yukle(secilen_lig_raw)
    
    if df_raw_base is not None:
        df_raw_agg = raw_data_hesapla(df_raw_base)
        
        st.dataframe(
            df_raw_agg, 
            use_container_width=True,
            column_config={
                "Gol Ort.": st.column_config.ProgressColumn("Gol Ort.", format="%.2f", min_value=0, max_value=3),
                "Yediği Gol Ort.": st.column_config.ProgressColumn("Yediği Gol Ort.", format="%.2f", min_value=0, max_value=3, color='#FF5252'),
                "Şut Ort.": st.column_config.ProgressColumn("Şut Ort.", format="%.1f", min_value=0, max_value=20),
                "Sarı Kart Ort.": st.column_config.ProgressColumn("Sarı Kart Ort.", format="%.1f", min_value=0, max_value=5),
            }
        )
        st.caption("Veriler, takımın iç saha ve deplasman maçlarının ortalaması alınarak hesaplanmıştır.")
    else:
        st.error("Ham veri yüklenemedi.")


# ================= SEKME 3: ASİSTAN =================
with tab3:
    st.markdown("### 🤖 ASİSTAN JARVIS")
    if "messages" not in st.session_state: st.session_state.messages = [{"role": "assistant", "content": "Selam! Maçları sorabilirsin."}]
    for msg in st.session_state.messages: st.chat_message(msg["role"]).write(msg["content"])
    if prompt := st.chat_input("Mesaj yaz..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        st.chat_message("assistant").write("Analiz sekmesinden detaylara bakabilirsin.")
