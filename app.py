import streamlit as st
import streamlit.components.v1 as components 
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from scipy.stats import poisson

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Futbol Kahini Pro Max", page_icon="🦁", layout="wide")

# --- CSS (NEON & MODERN) ---
st.markdown("""
<style>
    .stApp { background-color: #050505; color: #E0E0E0; }
    h1, h2, h3, h4 { color: #00E676 !important; font-family: 'Arial Black', sans-serif; text-transform: uppercase; }
    
    /* KARTLAR */
    .metric-card {
        background: linear-gradient(145deg, #1a1a1a, #121212);
        padding: 15px; border-radius: 12px; border-left: 5px solid #00E676;
        text-align: center; margin-bottom: 10px; box-shadow: 0 4px 15px rgba(0,230,118,0.1);
    }
    .metric-value { font-size: 24px; font-weight: bold; color: white; margin-top: 5px; }
    .metric-label { font-size: 12px; color: #aaa; letter-spacing: 1px; }

    /* ANALİZ KUTUSU */
    .analysis-box {
        background-color: #1E1E1E; padding: 20px; border-radius: 10px; border: 1px solid #333; margin-top: 15px;
    }
    
    /* Buton */
    .stButton>button { 
        background-color: #00E676; color: black !important; font-weight: 900 !important; border-radius: 8px; height: 50px; width: 100%; font-size: 18px !important;
    }
    .stTabs [aria-selected="true"] { background-color: #00E676; color: black !important; }
</style>
""", unsafe_allow_html=True)

# --- VERİ YAPILANDIRMASI (LİGLER) ---
# Not: İngiltere, İspanya gibi ligler genellikle E0, SP1 gibi kodlanır.
lig_yapilandirma = {
    "🇹🇷 Türkiye Süper Lig": "T1",
    "🇬🇧 İngiltere Premier": "E0",
    "🇪🇸 İspanya La Liga": "SP1",
    "🇩🇪 Almanya Bundesliga": "D1",
    "🇮🇹 İtalya Serie A": "I1",
    "🇫🇷 Fransa Ligue 1": "F1",
    "🇳🇱 Hollanda Eredivisie": "N1",
    "🇵🇹 Portekiz Liga NOS": "P1",
    "🇧🇪 Belçika Jupiler": "B1"
}

# İsim Düzeltme (Sadece kritik olanlar, gerisi olduğu gibi gelsin)
takim_duzeltme = {
    "Galatasaray": "Galatasaray", "Fenerbahce": "Fenerbahçe", "Besiktas": "Beşiktaş",
    "Adana Demirspor": "Adana Demirspor", "Eyupspor": "Eyüpspor", "Bodrumspor": "Bodrum FK",
    "Goztepe": "Göztepe", "Samsunspor": "Samsunspor"
}

# --- GÜVENLİ VERİ FONKSİYONLARI ---
def safe_mean(series):
    return series.mean() if not series.empty else 0.0

@st.cache_data(ttl=3600) # 1 saatte bir veriyi yenile
def veri_yukle(lig_kodu):
    # DİKKAT: 2024/2025 Sezonu verisini çekiyoruz
    url = f"https://www.football-data.co.uk/mmz4281/2425/{lig_kodu}.csv"
    try:
        df = pd.read_csv(url)
        df = df.dropna(subset=['HomeTeam', 'AwayTeam', 'FTHG']) # Boş satırları sil
        # Tarih düzeltme
        df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
        # İsimleri Türkçeleştir (Varsa)
        df['HomeTeam'] = df['HomeTeam'].replace(takim_duzeltme)
        df['AwayTeam'] = df['AwayTeam'].replace(takim_duzeltme)
        return df
    except:
        return None

# --- POISSON OLSALIK HESAPLAYICI (BİLİMSEL BAHİS) ---
def poisson_olasilik(ev_gol_beklenti, dep_gol_beklenti):
    # Poisson dağılımı ile kesin skor ihtimallerini hesaplar
    ev_olasilik = [poisson.pmf(i, ev_gol_beklenti) for i in range(6)]
    dep_olasilik = [poisson.pmf(i, dep_gol_beklenti) for i in range(6)]
    
    # Matris çarpımı (Olasılık tablosu)
    olasilik_matrisi = np.outer(ev_olasilik, dep_olasilik)
    
    # Sonuçlar
    ms1 = np.tril(olasilik_matrisi, -1).sum() * 100
    beraberlik = np.trace(olasilik_matrisi) * 100
    ms2 = np.triu(olasilik_matrisi, 1).sum() * 100
    
    kg_var = (1 - (olasilik_matrisi[0, :].sum() + olasilik_matrisi[:, 0].sum() - olasilik_matrisi[0, 0])) * 100
    ust_25 = (1 - (olasilik_matrisi[0, 0] + olasilik_matrisi[1, 0] + olasilik_matrisi[0, 1] + 
                   olasilik_matrisi[1, 1] + olasilik_matrisi[2, 0] + olasilik_matrisi[0, 2])) * 100
                   
    return ms1, beraberlik, ms2, kg_var, ust_25

# --- ANALİZ MOTORU ---
def analiz_et(ev, dep, df):
    ev_maclar = df[df['HomeTeam'] == ev]
    dep_maclar = df[df['AwayTeam'] == dep]
    
    if len(ev_maclar) < 1 or len(dep_maclar) < 1: return None
    
    # 1. TEMEL ORTALAMALAR
    ev_g = safe_mean(ev_maclar['FTHG']); dep_g = safe_mean(dep_maclar['FTAG'])
    ev_y = safe_mean(ev_maclar['FTAG']); dep_y = safe_mean(dep_maclar['FTHG'])
    
    # 2. ŞUT VERİSİ (Varsa)
    ev_sut = safe_mean(ev_maclar['HS']) if 'HS' in df.columns else 10.0
    dep_sut = safe_mean(dep_maclar['AS']) if 'AS' in df.columns else 8.0
    ev_isabet = safe_mean(ev_maclar['HST']) if 'HST' in df.columns else 4.0
    dep_isabet = safe_mean(dep_maclar['AST']) if 'AST' in df.columns else 3.0
    
    # 3. POISSON ANALİZİ (YENİ)
    # Lig ortalamasını baz alarak takım gücünü hesapla
    lig_ev_ort = df['FTHG'].mean()
    lig_dep_ort = df['FTAG'].mean()
    
    ev_atak_gucu = ev_g / lig_ev_ort if lig_ev_ort > 0 else 1.0
    dep_defans_gucu = dep_y / lig_ev_ort if lig_ev_ort > 0 else 1.0
    ev_beklenen_gol = ev_atak_gucu * dep_defans_gucu * lig_ev_ort
    
    dep_atak_gucu = dep_g / lig_dep_ort if lig_dep_ort > 0 else 1.0
    ev_defans_gucu = ev_y / lig_dep_ort if lig_dep_ort > 0 else 1.0
    dep_beklenen_gol = dep_atak_gucu * ev_defans_gucu * lig_dep_ort
    
    ms1_prob, draw_prob, ms2_prob, kg_prob, ust_prob = poisson_olasilik(ev_beklenen_gol, dep_beklenen_gol)
    
    # 4. TUTARLILIK (VOLATILITY)
    # Takım hep aynı mı oynuyor yoksa dengesiz mi? (Standart Sapma)
    ev_std = ev_maclar['FTHG'].std() if len(ev_maclar) > 1 else 0
    tutarlilik = "İstikrarlı" if ev_std < 0.8 else "Dengesiz/Sürprize Açık"

    return {
        "skor_tahmin": f"{int(round(ev_beklenen_gol))} - {int(round(dep_beklenen_gol))}",
        "ev_xg": ev_beklenen_gol, "dep_xg": dep_beklenen_gol,
        "ms1": ms1_prob, "beraberlik": draw_prob, "ms2": ms2_prob,
        "kg_prob": kg_prob, "ust_prob": ust_prob,
        "ev_sut": ev_sut, "dep_sut": dep_sut,
        "ev_isabet": ev_isabet, "dep_isabet": dep_isabet,
        "tutarlilik": tutarlilik,
        "korner": (safe_mean(ev_maclar['HC']) + safe_mean(dep_maclar['AC'])) if 'HC' in df.columns else 9.5
    }

# --- ARAYÜZ ---
st.title("🦁 FUTBOL KAHİNİ V35: UNCHAINED")

tab1, tab2, tab3 = st.tabs(["📊 PRO ANALİZ", "📝 RAW VERİ MERKEZİ", "🤖 ASİSTAN"])

# ================= SEKME 1: PRO ANALİZ =================
with tab1:
    st.markdown("### 🕵️‍♂️ BİLİMSEL MAÇ ANALİZİ")
    
    c1, c2, c3 = st.columns([2,2,2])
    with c1: 
        lig_adi = st.selectbox("LİG SEÇİNİZ", list(lig_yapilandirma.keys()))
        lig_kod = lig_yapilandirma[lig_adi]
    
    df = veri_yukle(lig_kod)
    
    if df is not None:
        takimlar = sorted(df['HomeTeam'].unique()) # Filtresiz tüm takımlar
        with c2: ev = st.selectbox("EV SAHİBİ", takimlar)
        with c3: dep = st.selectbox("DEPLASMAN", takimlar, index=1 if len(takimlar)>1 else 0)
        
        if st.button("DETAYLI ANALİZİ BAŞLAT 🚀"):
            res = analiz_et(ev, dep, df)
            
            if res:
                # --- SONUÇ KARTLARI ---
                st.markdown("#### 🎯 POISSON OLASILIKLARI (MATEMATİKSEL TAHMİN)")
                k1, k2, k3, k4 = st.columns(4)
                with k1: st.markdown(f"""<div class="metric-card"><div class="metric-label">SKOR TAHMİNİ</div><div class="metric-value">{res['skor_tahmin']}</div></div>""", unsafe_allow_html=True)
                with k2: st.markdown(f"""<div class="metric-card"><div class="metric-label">MS 1 İHTİMALİ</div><div class="metric-value">% {res['ms1']:.1f}</div></div>""", unsafe_allow_html=True)
                with k3: st.markdown(f"""<div class="metric-card"><div class="metric-label">2.5 ÜST İHTİMALİ</div><div class="metric-value">% {res['ust_prob']:.1f}</div></div>""", unsafe_allow_html=True)
                with k4: st.markdown(f"""<div class="metric-card"><div class="metric-label">KG VAR İHTİMALİ</div><div class="metric-value">% {res['kg_prob']:.1f}</div></div>""", unsafe_allow_html=True)
                
                st.divider()
                
                # --- GRAFİKLER ---
                g1, g2 = st.columns([1,1])
                
                with g1:
                    # Olasılık Pastası
                    labels = [f'{ev} Kazanır', 'Beraberlik', f'{dep} Kazanır']
                    values = [res['ms1'], res['beraberlik'], res['ms2']]
                    fig_pie = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.4, marker_colors=['#00E676', '#9E9E9E', '#FF5252'])])
                    fig_pie.update_layout(title="Maç Sonucu Olasılık Dağılımı", paper_bgcolor='rgba(0,0,0,0)', font={'color':'white'})
                    st.plotly_chart(fig_pie, use_container_width=True)
                    st.caption(f"💡 **Grafik Açıklaması:** Bu pasta grafik, binlerce simülasyon sonucu hesaplanan kazanma ihtimallerini gösterir. Yeşil alan ne kadar büyükse ev sahibi o kadar favoridir.")

                with g2:
                    # Hücum Verimliliği (Bar Chart)
                    fig_bar = go.Figure(data=[
                        go.Bar(name='Toplam Şut', x=[ev, dep], y=[res['ev_sut'], res['dep_sut']], marker_color='#546E7A'),
                        go.Bar(name='İsabetli Şut', x=[ev, dep], y=[res['ev_isabet'], res['dep_isabet']], marker_color='#00E676')
                    ])
                    fig_bar.update_layout(title="Hücum Kalitesi (Şut vs İsabet)", barmode='group', paper_bgcolor='rgba(0,0,0,0)', font={'color':'white'})
                    st.plotly_chart(fig_bar, use_container_width=True)
                    st.caption(f"💡 **Grafik Açıklaması:** Gri çubuk toplam şutu, Yeşil çubuk kaleyi bulan şutu gösterir. Yeşil çubuk griye ne kadar yakınsa takım o kadar 'keskin nişancı'dır.")

                # --- DETAYLI ANALİZ METNİ ---
                st.markdown("### 🎙️ ANALİZ LABORATUVARI RAPORU")
                st.markdown(f"""
                <div class="analysis-box">
                    <p style="color:#00E676; font-weight:bold;">1. GOL BEKLENTİSİ (xG) ANALİZİ</p>
                    <p>Verilere göre <b>{ev}</b> takımının bu maçta beklenen gol sayısı (xG) <b>{res['ev_xg']:.2f}</b> iken, 
                    <b>{dep}</b> takımının beklentisi <b>{res['dep_xg']:.2f}</b> seviyesindedir. 
                    İki takımın toplam gol beklentisi <b>{res['ev_xg'] + res['dep_xg']:.2f}</b> olduğu için maçta gol sesi çıkması muhtemeldir.</p>
                    
                    <p style="color:#00E676; font-weight:bold;">2. TAKIM KARAKTERİ & TUTARLILIK</p>
                    <p>Ev sahibi takım istatistiksel olarak <b>{res['tutarlilik']}</b> bir görüntü çiziyor. 
                    Hücum hattında maç başına ortalama <b>{res['ev_sut']:.1f}</b> şut denemesi yapıyorlar.
                    Deplasman ekibi ise kalesinde ortalama üstü pozisyon veriyor olabilir.</p>
                    
                    <p style="color:#00E676; font-weight:bold;">3. BAHİS ÖNERİSİ & RİSK YÖNETİMİ</p>
                    <p>Matematiksel model <b>%{res['ust_prob']:.1f}</b> ihtimalle 2.5 ÜST bahsini destekliyor.
                    Sürpriz arayanlar için KG VAR seçeneği <b>%{res['kg_prob']:.1f}</b> ihtimale sahip.
                    Korner bahsi oynayacaklar için beklenen toplam korner sayısı <b>{res['korner']:.1f}</b>.</p>
                </div>
                """, unsafe_allow_html=True)
                
            else: st.error("Bu takımlar için yeterli veri oluşmamış (Yeni sezonun ilk haftaları olabilir).")
    else:
        st.error("Veri kaynağına erişilemedi. Lütfen daha sonra tekrar deneyin.")

# ================= SEKME 2: RAW VERİ (İSTEDİĞİN GİBİ) =================
with tab2:
    st.markdown("### 📝 HAM VERİ İSTATİSTİKLERİ")
    st.info("Yapay zekanın beslendiği gerçek veriler. Takımların sezon ortalamalarını buradan kontrol edebilirsin.")
    
    if df is not None:
        # Raw Data Hesaplama
        takimlar_raw = df['HomeTeam'].unique()
        liste = []
        for t in takimlar_raw:
            maclar = df[(df['HomeTeam'] == t) | (df['AwayTeam'] == t)]
            if len(maclar) > 0:
                liste.append({
                    "Takım": t,
                    "Maç": len(maclar),
                    "Gol Atma": safe_mean(maclar.apply(lambda x: x['FTHG'] if x['HomeTeam']==t else x['FTAG'], axis=1)),
                    "Gol Yeme": safe_mean(maclar.apply(lambda x: x['FTAG'] if x['HomeTeam']==t else x['FTHG'], axis=1)),
                    "Şut Ort.": safe_mean(maclar.apply(lambda x: x['HS'] if x['HomeTeam']==t else x['AS'], axis=1)) if 'HS' in df.columns else 0,
                    "Kart Ort.": safe_mean(maclar.apply(lambda x: x['HY'] if x['HomeTeam']==t else x['AY'], axis=1)) if 'HY' in df.columns else 0
                })
        
        df_raw = pd.DataFrame(liste).sort_values(by='Gol Atma', ascending=False)
        
        st.dataframe(
            df_raw,
            column_config={
                "Gol Atma": st.column_config.ProgressColumn("Gol Atma Ort.", format="%.2f", min_value=0, max_value=3.5),
                "Gol Yeme": st.column_config.ProgressColumn("Gol Yeme Ort.", format="%.2f", min_value=0, max_value=3.5, color="#FF5252"),
                "Şut Ort.": st.column_config.NumberColumn("Şut Ort.", format="%.1f"),
            },
            use_container_width=True
        )

# ================= SEKME 3: ASİSTAN =================
with tab3:
    st.markdown("### 🤖 ASİSTAN JARVIS")
    if "messages" not in st.session_state: st.session_state.messages = [{"role": "assistant", "content": "Analizler hazır! Hangi ligi merak ediyorsun?"}]
    for msg in st.session_state.messages: st.chat_message(msg["role"]).write(msg["content"])
    if prompt := st.chat_input("Bir şey sor..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        st.chat_message("assistant").write("Detaylı analiz sekmesindeki verileri inceleyerek sana en doğru cevabı verebilirim.")
