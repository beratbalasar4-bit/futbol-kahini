import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.graph_objects as go
import datetime

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Futbol Kahini Pro", page_icon="⚽", layout="wide")

# --- CSS (NEON VE DETAYLI TASARIM) ---
st.markdown("""
<style>
    /* Ana Arka Plan */
    .stApp { background-color: #0E1117; color: #E0E0E0; }
    
    /* Başlıklar */
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
    
    /* Form Kutucukları (G/B/M) */
    .form-badge { display: inline-block; width: 35px; height: 35px; line-height: 35px; text-align: center; border-radius: 5px; font-weight: bold; color: white; margin-right: 5px; font-size: 14px; }
    .win { background-color: #00E676; color: black; }
    .draw { background-color: #9E9E9E; }
    .loss { background-color: #FF5252; }
    
    /* Açıklama Kutusu */
    .desc-box { background-color: #263238; border-left: 4px solid #00E676; padding: 15px; border-radius: 5px; font-size: 14px; line-height: 1.5; color: white !important; }

    /* Buton */
    .stButton>button { background-color: #00E676; color: black !important; font-weight: 900 !important; border-radius: 8px; height: 55px; border: 2px solid #00C853; width: 100%; font-size: 20px !important; box-shadow: 0 0 15px rgba(0, 230, 118, 0.4); }
    .stButton>button:hover { background-color: #00C853; color: white !important; transform: scale(1.02); }
    
    /* Sekme */
    .stTabs [aria-selected="true"] { background-color: #00E676; color: black !important; font-weight: bold; border-radius: 5px; }
</style>
""", unsafe_allow_html=True)

# --- LİNKLER (PUAN DURUMU İÇİN CANLI LİNKLER) ---
standings_urls = {
    "🇹🇷 Türkiye Süper Lig": "https://www.livescore.bz/en/football/turkey/super-lig/standings/",
    "🇬🇧 İngiltere Premier": "https://www.livescore.bz/en/football/england/premier-league/standings/",
    "🇪🇸 İspanya La Liga": "https://www.livescore.bz/en/football/spain/laliga/standings/",
    "🇩🇪 Almanya Bundesliga": "https://www.livescore.bz/en/football/germany/bundesliga/standings/",
    "🇮🇹 İtalya Serie A": "https://www.livescore.bz/en/football/italy/serie-a/standings/",
    "🇫🇷 Fransa Ligue 1": "https://www.livescore.bz/en/football/france/ligue-1/standings/",
    "🇳🇱 Hollanda Eredivisie": "https://www.livescore.bz/en/football/netherlands/eredivisie/standings/",
    "🇵🇹 Portekiz Liga NOS": "https://www.livescore.bz/en/football/portugal/primeira-liga/standings/"
}

# --- VERİ SETLERİ (ANALİZ İÇİN CSV) ---
lig_kodlari = {
    "🇹🇷 Türkiye Süper Lig": "T1.csv", "🇬🇧 İngiltere Premier": "E0.csv", 
    "🇪🇸 İspanya La Liga": "SP1.csv", "🇩🇪 Almanya Bundesliga": "D1.csv", 
    "🇮🇹 İtalya Serie A": "I1.csv", "🇫🇷 Fransa Ligue 1": "F1.csv",
    "🇳🇱 Hollanda Eredivisie": "N1.csv", "🇵🇹 Portekiz Liga NOS": "P1.csv"
}

takim_duzeltme = {
    "Fenerbahce": "Fenerbahçe", "Galatasaray": "Galatasaray", "Besiktas": "Beşiktaş", "Trabzonspor": "Trabzonspor",
    "Buyuksehyr": "Başakşehir", "Man City": "Man City", "Man United": "Man Utd",
    "Real Madrid": "R. Madrid", "Barcelona": "Barcelona", "Bayern Munich": "Bayern",
    "Dortmund": "Dortmund", "Paris SG": "PSG", "Inter": "Inter", "Milan": "Milan", "Juventus": "Juve",
    "Benfica": "Benfica", "Porto": "Porto", "Ajax": "Ajax"
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

# --- FORM HESAPLAMA (SON 5 MAÇ) ---
def form_getir(takim, df):
    # Takımın son 5 maçını bul
    maclar = df[(df['HomeTeam'] == takim) | (df['AwayTeam'] == takim)].tail(5)
    sonuclar = []
    
    for _, row in maclar.iterrows():
        if row['HomeTeam'] == takim:
            if row['FTR'] == 'H': sonuclar.append("G")
            elif row['FTR'] == 'D': sonuclar.append("B")
            else: sonuclar.append("M")
        else: # Deplasman
            if row['FTR'] == 'A': sonuclar.append("G")
            elif row['FTR'] == 'D': sonuclar.append("B")
            else: sonuclar.append("M")
    return sonuclar

# --- ANALİZ MOTORU ---
def analiz_motoru(ev, dep, df):
    ev_stats = df[df['HomeTeam'] == ev]
    dep_stats = df[df['AwayTeam'] == dep]
    if len(ev_stats) < 1 or len(dep_stats) < 1: return None

    # İstatistikler
    ev_gol_at = ev_stats['FTHG'].mean()
    dep_gol_at = dep_stats['FTAG'].mean()
    ev_gol_ye = ev_stats['FTAG'].mean()
    dep_gol_ye = dep_stats['FTHG'].mean()
    
    # Baskı (Şut)
    ev_baski = 50; dep_baski = 50
    if 'HS' in df.columns:
        ev_score = ev_stats['HS'].mean()
        dep_score = dep_stats['AS'].mean()
        toplam = ev_score + dep_score
        ev_baski = (ev_score / toplam) * 100
        dep_baski = (dep_score / toplam) * 100

    # Korner
    ev_korner = ev_stats['HC'].mean() if 'HC' in df.columns else 4.5
    dep_korner = dep_stats['AC'].mean() if 'AC' in df.columns else 4.0
    toplam_korner = ev_korner + dep_korner
    
    # Kart
    ev_kart = ev_stats['HY'].mean() + ev_stats['AY'].mean() if 'HY' in df.columns else 2.0
    dep_kart = dep_stats['HY'].mean() + dep_stats['AY'].mean() if 'HY' in df.columns else 2.0
    toplam_kart = (ev_kart + dep_kart) / 2
    
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
        "ev_gol": ev_gol_at, "dep_gol": dep_gol_at, "ev_yed": ev_gol_ye, "dep_yed": dep_gol_ye,
        "kart": toplam_kart
    }

# --- ARAYÜZ ---
st.title("🦁 FUTBOL KAHİNİ V21")

tab_analiz, tab_puan, tab_live, tab_chat = st.tabs(["📊 DETAYLI ANALİZ", "🏆 PUAN DURUMU", "📺 CANLI SKOR", "🤖 ASİSTAN"])

# ================= SEKME 1: ULTRA DETAYLI ANALİZ =================
with tab_analiz:
    st.markdown("### 🕵️‍♂️ MAÇ ANALİZ MERKEZİ")
    
    # 1. SEÇİM
    c1, c2, c3 = st.columns([2,2,2])
    with c1: secilen_lig = st.selectbox("LİG SEÇİNİZ", list(lig_kodlari.keys()))
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
                
                # --- KISIM 1: SON 5 MAÇ (FORM DURUMU) ---
                st.markdown("#### 📈 TAKIMLARIN FORM DURUMU")
                f1, f2 = st.columns(2)
                
                ev_form = form_getir(ev, df)
                dep_form = form_getir(dep, df)
                
                def form_html(liste):
                    html = ""
                    for x in liste:
                        renk = "win" if x == "G" else ("loss" if x == "M" else "draw")
                        html += f"<div class='form-badge {renk}'>{x}</div>"
                    return html
                
                with f1:
                    st.markdown(f"**{ev} (Son 5 Maç):**")
                    st.markdown(form_html(ev_form), unsafe_allow_html=True)
                with f2:
                    st.markdown(f"**{dep} (Son 5 Maç):**")
                    st.markdown(form_html(dep_form), unsafe_allow_html=True)
                
                st.divider()

                # --- KISIM 2: ANA TAHMİNLER ---
                k1, k2, k3, k4 = st.columns(4)
                with k1: st.markdown(f"""<div class="stat-card"><div class="card-title">SKOR TAHMİNİ</div><div class="big-score">{res['skor']}</div></div>""", unsafe_allow_html=True)
                with k2: st.markdown(f"""<div class="stat-card"><div class="card-title">KAZANMA ŞANSI</div><div class="big-score">% {res['ibre']:.0f}</div></div>""", unsafe_allow_html=True)
                with k3: st.markdown(f"""<div class="stat-card"><div class="card-title">GOL BARAJI</div><div class="big-score" style="font-size:22px;">{res['alt_ust']}</div></div>""", unsafe_allow_html=True)
                with k4: st.markdown(f"""<div class="stat-card"><div class="card-title">KG (KARŞILIKLI)</div><div class="big-score" style="font-size:22px;">{res['kg']}</div></div>""", unsafe_allow_html=True)

                # --- KISIM 3: İSTATİSTİK KARŞILAŞTIRMA (Bar Chart) ---
                st.markdown("#### ⚔️ İSTATİSTİK SAVAŞI")
                g1, g2 = st.columns(2)
                
                with g1:
                    # Gol Atma/Yeme Grafiği
                    fig_stats = go.Figure(data=[
                        go.Bar(name='Gol Atma Ort.', x=[ev, dep], y=[res['ev_gol'], res['dep_gol']], marker_color='#00E676'),
                        go.Bar(name='Gol Yeme Ort.', x=[ev, dep], y=[res['ev_yed'], res['dep_yed']], marker_color='#FF5252')
                    ])
                    fig_stats.update_layout(title="Gol Performansı (Maç Başı)", barmode='group', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font={'color':'white'}, height=250)
                    st.plotly_chart(fig_stats, use_container_width=True)
                
                with g2:
                    # Korner/Kart Grafiği
                    fig_kk = go.Figure(data=[
                        go.Bar(name='Korner', x=[ev, dep], y=[res['ev_korner'], res['dep_korner']], marker_color='#F1C40F'),
                        go.Bar(name='Kart/Sertlik', x=[ev, dep], y=[res['kart'], res['kart']], marker_color='#9E9E9E') 
                    ])
                    fig_kk.update_layout(title="Oyun İstatistikleri", barmode='group', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font={'color':'white'}, height=250)
                    st.plotly_chart(fig_kk, use_container_width=True)

                # --- KISIM 4: RADAR VE BASKI ---
                r1, r2 = st.columns([1, 1])
                with r1:
                    # Radar
                    categories = ['Hücum', 'Korner', 'Baskı', 'Gol Beklentisi']
                    fig_radar = go.Figure()
                    fig_radar.add_trace(go.Scatterpolar(r=[res['ev_gol']*20, res['ev_korner']*10, res['ev_baski'], res['ev_gol']*25], theta=categories, fill='toself', name=ev, line_color='#00E676'))
                    fig_radar.add_trace(go.Scatterpolar(r=[res['dep_gol']*20, res['dep_korner']*10, res['dep_baski'], res['dep_gol']*25], theta=categories, fill='toself', name=dep, line_color='#FF5252'))
                    fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font={'color':'white'}, height=250, margin=dict(t=30, b=20, l=20, r=20), title="Güç Dağılımı")
                    st.plotly_chart(fig_radar, use_container_width=True)
                
                with r2:
                     st.markdown(f"""
                     <div class="desc-box" style="margin-top: 50px;">
                     <b>🤖 YAPAY ZEKA YORUMU:</b><br><br>
                     Verilere baktığımda <b>{ev}</b> takımının evindeki baskı gücü %{res['ev_baski']:.0f} seviyesinde. 
                     <b>{dep}</b> ise deplasmanda ortalama {res['dep_gol']:.1f} gol atabiliyor.<br><br>
                     Maçın <b>{res['alt_ust']}</b> bitme ihtimali yüksek. Kornerlerde ise toplam {res['toplam_korner']:.1f} barajı zorlanabilir.
                     </div>
                     """, unsafe_allow_html=True)

            else: st.error("Veri yetersiz.")

# ================= SEKME 2: PUAN DURUMU (IFRAME İLE KESİN ÇÖZÜM) =================
with tab_puan:
    st.markdown(f"### 🏆 GÜNCEL PUAN DURUMU")
    
    # Seçilen lige göre doğru linki getir
    link = standings_urls.get(secilen_lig, "https://www.livescore.bz")
    
    # Iframe ile canlı siteyi gömüyoruz
    components.html(f"""
    <iframe src="{link}" width="100%" height="800" frameborder="0" style="background-color: white; border-radius: 10px;"></iframe>
    """, height=800, scrolling=True)

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
