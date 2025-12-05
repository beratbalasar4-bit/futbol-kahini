import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import datetime
import random
import numpy as np

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Futbol Kahini Master", page_icon="⚽", layout="wide")

# --- CSS (NEON TASARIM) ---
st.markdown("""
<style>
    /* GENEL */
    .stApp { background-color: #050505; color: #E0E0E0; }
    h1, h2, h3, h4 { color: #00E676 !important; font-family: 'Arial Black', sans-serif; text-transform: uppercase; letter-spacing: 1px; }
    
    /* YORUM KUTUSU */
    .tactic-box {
        background-color: #1E1E1E; padding: 20px; border-radius: 12px; border: 1px solid #333; margin-top: 10px;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important; 
        font-size: 16px; line-height: 1.6; color: #ddd; 
    }
    .tactic-header { color: #00E676; font-weight: bold; font-size: 18px; border-bottom: 1px solid #444; padding-bottom: 10px; margin-bottom: 10px; }
    
    /* KARTLAR */
    .metric-card {
        background: linear-gradient(145deg, #1a1a1a, #121212);
        padding: 15px; border-radius: 10px; border-left: 5px solid #00E676;
        text-align: center; margin-bottom: 10px; box-shadow: 0 4px 15px rgba(0,230,118,0.1);
    }
    .metric-value { font-size: 24px; font-weight: bold; color: white; margin-top: 5px; }

    /* Buton */
    .stButton>button { background-color: #00E676; color: black !important; font-weight: 900 !important; border-radius: 8px; height: 55px; border: 2px solid #00C853; width: 100%; font-size: 20px !important; box-shadow: 0 0 15px rgba(0, 230, 118, 0.4); }
    .stTabs [aria-selected="true"] { background-color: #00E676; color: black !important; font-weight: bold; border-radius: 5px; }
</style>
""", unsafe_allow_html=True)

# --- VERİ VE FONKSİYON YAPILANDIRMASI ---

# YENİ KAPSAM: Sadece 7 Büyük Lig
lig_yapilandirma = {
    "🇹🇷 Türkiye Süper Lig": {"csv": "T1.csv", "live": "https://www.flashscore.mobi/standings/W6BOzpK2/U3MvIVsA/#table/overall"},
    "🇬🇧 İngiltere Premier": {"csv": "E0.csv", "live": "https://www.flashscore.mobi/standings/dYlOSQ44/W6DOvJ92/#table/overall"},
    "🇪🇸 İspanya La Liga": {"csv": "SP1.csv", "live": "https://www.flashscore.mobi/standings/QVmLl54o/dG2SqPPf/#table/overall"},
    "🇩🇪 Almanya Bundesliga": {"csv": "D1.csv", "live": "https://www.flashscore.mobi/standings/W6BOzpK2/U3MvIVsA/#table/overall"},
    "🇮🇹 İtalya Serie A": {"csv": "I1.csv", "live": "https://www.flashscore.mobi/standings/dYlOSQ44/W6DOvJ92/#table/overall"},
    "🇫🇷 Fransa Ligue 1": {"csv": "F1.csv", "live": "https://www.flashscore.mobi/standings/W6BOzpK2/U3MvIVsA/#table/overall"},
    "🇵🇹 Portekiz Liga NOS": {"csv": "P1.csv", "live": "https://www.flashscore.mobi"}
}

# GÜNCEL TAKIM LİSTELERİ (Eksik takımları eliyoruz)
GUNCEL_TAKIMLAR = {
    "🇹🇷 Türkiye Süper Lig": ["Fenerbahçe", "Galatasaray", "Beşiktaş", "Trabzonspor", "Başakşehir", "Kasımpaşa", "Kocaelispor", "Konyaspor", "Kayserispor", "Gaziantep", "Sivasspor", "Alanyaspor", "Antalyaspor", "Hatayspor", "Samsunspor", "Göztepe", "Eyüpspor"],
    "🇬🇧 İngiltere Premier": ["Man City", "Arsenal", "Liverpool", "Aston Villa", "Tottenham", "Chelsea", "Man Utd", "Newcastle", "Leicester", "Ipswich", "Southampton", "Crystal Palace", "Wolves", "Bournemouth", "Fulham", "Everton", "Brighton", "West Ham"],
    "🇩🇪 Almanya Bundesliga": ["Bayern Munich", "Dortmund", "Leverkusen", "Stuttgart", "RB Leipzig", "Eintracht Frankfurt", "Hoffenheim", "Freiburg", "Augsburg", "Werder Bremen", "Wolfsburg", "Mainz", "Union Berlin", "Bochum", "Heidenheim", "Holstein Kiel", "St. Pauli", "Fortuna Düsseldorf"],
    "🇪🇸 İspanya La Liga": ["R. Madrid", "Barcelona", "Girona", "Atl. Madrid", "Athletic Club", "Real Sociedad", "Betis", "Valencia", "Villarreal", "Getafe", "Alavés", "Sevilla", "Osasuna", "Celta Vigo", "Rayo Vallecano", "Mallorca", "Leganés", "Valladolid"],
    "🇮🇹 İtalya Serie A": ["Inter", "Milan", "Juventus", "Bologna", "Atalanta", "Roma", "Lazio", "Fiorentina", "Torino", "Monza", "Genoa", "Empoli", "Verona", "Udinese", "Cagliari", "Lecce", "Como", "Venezia"],
    "🇫🇷 Fransa Ligue 1": ["PSG", "Monaco", "Brest", "Lille", "Nice", "Lens", "Lyon", "Marseille", "Rennes", "Toulouse", "Montpellier", "Strasbourg", "Nantes", "Lorient", "St Etienne", "Auxerre", "Angers", "Le Havre"],
    "🇵🇹 Portekiz Liga NOS": ["Benfica", "Porto", "Sporting CP", "Braga", "Vitoria Guimaraes", "Arouca", "Moreirense", "Farense", "Estoril", "Vizela", "Marítimo", "Académico Viseu", "Penafiel", "Rio Ave", "Boavista", "Casa Pia", "Famalicão", "Portimonense"]
}

takim_duzeltme = {
    "Fenerbahce": "Fenerbahçe", "Galatasaray": "Galatasaray", "Besiktas": "Beşiktaş", "Trabzonspor": "Trabzonspor",
    "Man City": "Man City", "Man United": "Man Utd", "Real Madrid": "R. Madrid", "Barcelona": "Barcelona", 
    "Bayern Munich": "Bayern Munich", "Dortmund": "Dortmund", "Kocaeli": "Kocaelispor", "Eyup": "Eyüpspor"
}

# HATA DÜZELTME: Güvenli Ortalama Alma
def get_safe_mean(df_slice, col_name, default=0.0):
    if col_name in df_slice.columns:
        mean_val = df_slice[col_name].mean()
        return mean_val if pd.notna(mean_val) else default
    return default

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
        
        # GÜNCEL TAKIM FİLTRESİ
        current_teams = GUNCEL_TAKIMLAR.get(lig_ad, df['HomeTeam'].unique())
        df = df[df['HomeTeam'].isin(current_teams) & df['AwayTeam'].isin(current_teams)]
        
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
        
        if O == 0: continue
        
        avg_data = {"Takım": team, "Oynanan Maç": O}
        
        avg_data["Gol Ort."] = (home['FTHG'].sum() + away['FTAG'].sum()) / O
        avg_data["Yediği Gol Ort."] = (home['FTAG'].sum() + away['FTHG'].sum()) / O
        
        # Güvenli ortalama alımı
        avg_data["Şut Ort."] = (get_safe_mean(home, 'HS') + get_safe_mean(away, 'AS')) / 2
        avg_data["İsabetli Şut Ort."] = (get_safe_mean(home, 'HST') + get_safe_mean(away, 'AST')) / 2
        avg_data["Faul Ort."] = (get_safe_mean(home, 'HF') + get_safe_mean(away, 'AF')) / 2
        avg_data["Sarı Kart Ort."] = (get_safe_mean(home, 'HY') + get_safe_mean(away, 'AY')) / 2
            
        raw_stats.append(avg_data)
        
    df_raw = pd.DataFrame(raw_stats).sort_values(by='Gol Ort.', ascending=False).reset_index(drop=True)
    df_raw.index += 1
    return df_raw

# --- TAKTİK VE ANALİZ MOTORLARI ---

def taktik_analiz(stats, taraf="Ev"):
    gol_at = get_safe_mean(stats, 'FTHG' if taraf == "Ev" else 'FTAG')
    gol_ye = get_safe_mean(stats, 'FTAG' if taraf == "Ev" else 'FTHG')
    kart = get_safe_mean(stats, 'HY') + get_safe_mean(stats, 'AY')
    
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
    
    ev_faul_ort = get_safe_mean(ev_stats, 'HF', default=10.0); dep_faul_ort = get_safe_mean(dep_stats, 'AF', default=10.0)

    toplam_korner = get_safe_mean(ev_stats, 'HC', default=5.0) + get_safe_mean(dep_stats, 'AC', default=4.0)
    toplam_kart = get_safe_mean(ev_stats, 'HY') + get_safe_mean(dep_stats, 'AY')
    
    # Yeni Metrikler
    sut_isabet_yuzdesi_ev = (ev_shot_target / ev_total_shot) * 100 if ev_total_shot > 0 else 0
    sut_isabet_yuzdesi_dep = (dep_shot_target / dep_total_shot) * 100 if dep_total_shot > 0 else 0
    gol_basina_sut_ev = ev_total_shot / ev_gol_at if ev_gol_at > 0 else 99
    gol_basina_sut_dep = dep_total_shot / dep_gol_at if dep_gol_at > 0 else 99

    # TAHMİNLER
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
        "double_chance": f"1X ({ev} veya Berabere)" if ibre > 45 else f"X2 (Berabere veya {dep})",
        "sut_isabet_yuzdesi_ev": sut_isabet_yuzdesi_ev, "sut_isabet_yuzdesi_dep": sut_isabet_yuzdesi_dep,
        "gol_basina_sut_ev": gol_basina_sut_ev, "gol_basina_sut_dep": gol_basina_sut_dep,
        "ev_faul_ort": ev_faul_ort, "dep_faul_ort": dep_faul_ort
    }

# --- ARAYÜZ ---
st.title("🦁 FUTBOL KAHİNİ V32")

# HATA DÜZELTİLDİ: 4 sekme doğru tanımlanıyor.
tab1, tab2, tab3, tab4 = st.tabs(["📊 DETAYLI ANALİZ", "📝 RAW İSTATİSTİK MERKEZİ", "📺 CANLI SKOR", "🤖 ASİSTAN"]) 

# ================= SEKME 1: MAKSİMUM DETAYLI ANALİZ =================
with tab1:
    st.markdown("### 🕵️‍♂️ MAÇ ANALİZ ROBOTU")
    st.info(f"📅 Bu analiz, 5 Aralık 2025 tarihli **mevcut veri tabanı** kullanılarak yapılmıştır. Tüm takımlar analiz edilebilir.")

    c1, c2, c3 = st.columns([2,2,2])
    with c1: secilen_lig = st.selectbox("LİG SEÇİNİZ", list(lig_yapilandirma.keys()), key="analiz_lig")
    df = veri_yukle(secilen_lig)
    
    if df is not None:
        takimlar = sorted(df['HomeTeam'].unique())
        with c2: ev = st.selectbox("EV SAHİBİ", takimlar, key="analiz_ev")
        with c3: dep = st.selectbox("DEPLASMAN", takimlar, index=1, key="analiz_dep")
        
        # CANLI FORM GÖRÜNTÜLEYİCİ
        with st.expander("📡 Canlı Form Doğrulama (Tıkla Aç)", expanded=False):
            st.caption("Analizi doğrulamak için Flashscore'dan anlık veri.")
            link_canli = lig_yapilandirma.get(secilen_lig, {}).get('live', 'https://www.flashscore.mobi')
            components.html(f"""<iframe src="{link_canli}" width="100%" height="300" frameborder="0" style="background:white;"></iframe>""", height=300)

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
                    <div class="tactic-header">MAÇ SENARYOSU VE OYUN ANLAYIŞI</div>
                    <p class="tactic-text">
                        <b>{ev}</b> takımı genel olarak **{ev_stil}** oyun stilini tercih ediyor. Ev sahibinin şut isabet yüzdesi **% {res['sut_isabet_yuzdesi_ev']:.1f}** ile rakipten **% {res['sut_isabet_yuzdesi_dep']:.1f}** daha verimli.
                        <br><br>
                        <b>{dep}</b> takımı ise deplasmanda **{dep_stil}** yaklaşımla sahada yer alacaktır. Beklenen korner sayısı **{res['korner_tahmin']:.1f}** ve maçın faul ortalaması **{res['ev_faul_ort'] + res['dep_faul_ort']:.1f}** seviyesinde seyredecektir.
                    </p>
                </div>
                """, unsafe_allow_html=True)

                # --- BÖLÜM 2: MAKSİMUM BAHİS PROJEKSİYONLARI ---
                st.markdown("#### 🎯 EKSTRA BAHİS PROJEKSİYONLARI")
                
                p1, p2, p3, p4 = st.columns(4)
                
                with p1:
                    st.markdown(f"""<div class="metric-card"><div class="metric-title">GOL BAŞINA ŞUT (Verim)</div><div class="metric-value">{res['gol_basina_sut_ev']:.1f} ({ev})</div></div>""", unsafe_allow_html=True)
                with p2:
                    st.markdown(f"""<div class="metric-card"><div class="metric-title">DİSİPLİN RİSKİ (Faul Ort.)</div><div class="metric-value">{res['ev_faul_ort']:.1f} / {res['dep_faul_ort']:.1f}</div></div>""", unsafe_allow_html=True)
                with p3:
                    st.markdown(f"""<div class="metric-card"><div class="metric-title">DEVRE/MAÇ SONUCU</div><div class="metric-value">{'1/1' if res['ibre'] > 65 else 'X/1'}</div></div>""", unsafe_allow_html=True)
                with p4:
                    st.markdown(f"""<div class="metric-card"><div class="metric-title">ÇİFTE ŞANS TAHMİNİ</div><div class="metric-value">{res['double_chance']}</div></div>""", unsafe_allow_html=True)
                
                # --- GRAFİKLER (MAX DETAY) ---
                st.markdown("### 📊 GRAFİKSEL VERİ KARŞILAŞTIRMASI")

                g1, g2 = st.columns([1, 1])
                with g1:
                    # Radar Grafiği
                    categories = ['Hücum', 'Savunma', 'Şut Ort.', 'İsabet Yüzdesi']
                    fig_radar = go.Figure()
                    fig_radar.add_trace(go.Scatterpolar(r=[res['ev_gol']*20, res['ev_yed']*15, res['ev_sut_ort']*3, res['sut_isabet_yuzdesi_ev']], theta=categories, fill='toself', name=ev, line_color='#00E676'))
                    fig_radar.add_trace(go.Scatterpolar(r=[res['dep_gol']*20, res['dep_yed']*15, res['dep_sut_ort']*3, res['sut_isabet_yuzdesi_dep']], theta=categories, fill='toself', name=dep, line_color='#FF5252'))
                    fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), title="Takım Güç Profili (Yüzde)", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font={'color':'white'}, height=300)
                    st.plotly_chart(fig_radar, use_container_width=True)

                with g2:
                    # Basketbar Grafiği (Şut vs İsabetli Şut)
                    df_baski = pd.DataFrame({
                        'Takım': [ev, dep, ev, dep],
                        'Tip': ['Toplam Şut', 'Toplam Şut', 'İsabetli Şut', 'İsabetli Şut'],
                        'Ortalama': [res['ev_sut_ort'], res['dep_sut_ort'], res['ev_sut_isabet'], res['dep_sut_isabet']],
                        'Renk': ['Toplam', 'Toplam', 'İsabet', 'İsabet']
                    })
                    fig_baski = px.bar(df_baski, x='Takım', y='Ortalama', color='Tip', barmode='group',
                                       title="Hücum Kalitesi ve Yoğunluğu", color_discrete_map={'Toplam Şut': '#B0BEC5', 'İsabetli Şut': '#00E676'})
                    fig_baski.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font={'color':'white'}, height=300)
                    st.plotly_chart(fig_baski, use_container_width=True)
                
                # YENİ EK: SAVUNMA ZAFİYETLERİ
                st.markdown("#### 🛡️ SAVUNMA VE DİSİPLİN ANALİZİ")
                s1, s2 = st.columns(2)
                with s1:
                    st.info(f"Gol/Şut Verimi: **{ev}** gol atmak için **{res['gol_basina_sut_ev']:.1f}** şut atarken, **{dep}** takımı **{res['gol_basina_sut_dep']:.1f}** şut atıyor. (Düşük sayı = Daha Verimli)")
                with s2:
                    st.info(f"Disiplin: Maç başı faul ortalaması **{ev}** için **{res['ev_faul_ort']:.1f}**, **{dep}** için **{res['dep_faul_ort']:.1f}**. (Yüksek sayı = Daha Sert Oyun)")


            else: st.error("Veri yetersiz.")

# ================= SEKME 2: RAW İSTATİSTİK MERKEZİ =================
with tab2:
    st.markdown("### 📝 TAKIM ORTALAMA İSTATİSTİKLERİ")
    st.info("Bu tabloda Yapay Zekanın kullandığı **işlenmiş ortalama ham veri** (Maç Başı) yer alır. Takım takım ortalamalar listelenmiştir.")
    
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


# ================= SEKME 3: CANLI SKOR =================
with tab3:
    st.markdown("### 📺 CANLI MAÇ MERKEZİ")
    components.html("""<iframe src="https://www.livescore.bz" width="100%" height="800" frameborder="0" style="background-color: white; border-radius: 8px;"></iframe>""", height=800, scrolling=True)

# ================= SEKME 4: ASİSTAN =================
with tab4:
    st.markdown("### 🤖 ASİSTAN JARVIS")
    if "messages" not in st.session_state: st.session_state.messages = [{"role": "assistant", "content": "Selam! Maçları sorabilirsin."}]
    for msg in st.session_state.messages: st.chat_message(msg["role"]).write(msg["content"])
    if prompt := st.chat_input("Mesaj yaz..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        st.chat_message("assistant").write("Analiz sekmesinden detaylara bakabilirsin.")
