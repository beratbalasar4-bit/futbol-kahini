import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import datetime

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Futbol Kahini Master", page_icon="🦁", layout="wide")

# --- CSS (OKUNABİLİRLİK VE KONTRAST ODAKLI) ---
st.markdown("""
<style>
    /* Genel Arka Plan */
    .stApp { background-color: #0E1117; }
    
    /* Yazı Renkleri - Okunabilirlik için Beyaz */
    h1, h2, h3, h4, p, span, div { color: #FAFAFA !important; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    
    /* Özel Renkli Başlıklar */
    .highlight { color: #00E676 !important; font-weight: bold; }
    
    /* Analiz Kartları */
    .analiz-card {
        background-color: #1F2937; 
        padding: 20px; 
        border-radius: 12px; 
        border: 1px solid #374151;
        margin-bottom: 20px;
    }
    
    /* Bahis Tablosu Satırları */
    .bet-row {
        display: flex; justify-content: space-between; align-items: center;
        padding: 12px; border-bottom: 1px solid #374151;
    }
    .bet-title { font-weight: bold; color: #B0BEC5 !important; }
    .bet-val { font-weight: bold; color: #00E676 !important; font-size: 18px; }
    .bet-val-risk { color: #FF5252 !important; }
    
    /* Seçim Kutuları */
    .stSelectbox label { color: #00E676 !important; font-weight: bold; }
    
    /* Buton */
    .stButton>button { 
        background: linear-gradient(to right, #00C853, #64DD17); 
        color: black !important; 
        width: 100%; 
        border-radius: 8px; 
        height: 50px; 
        font-weight: 800; 
        border: none;
        font-size: 18px;
    }
    .stButton>button:hover { opacity: 0.9; }
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

# --- MANTIKLI ANALİZ MOTORU ---
def mantikli_analiz(ev, dep, df):
    ev_stats = df[df['HomeTeam'] == ev]
    dep_stats = df[df['AwayTeam'] == dep]
    
    if len(ev_stats) < 2 or len(dep_stats) < 2: return None

    # 1. GOL BEKLENTİSİ HESABI (Tutarlılık için en önemli kısım)
    # Ev sahibi evinde ne atıyor + Deplasman dışarıda ne yiyor -> Ortalaması
    ev_beklenti = (ev_stats['FTHG'].mean() + dep_stats['FTAG'].mean()) / 2
    dep_beklenti = (dep_stats['FTAG'].mean() + ev_stats['FTHG'].mean()) / 2 # Düzeltme: Deplasman atar + Ev yer
    
    # 2. SKOR TAHMİNİ (Yuvarlama)
    skor_ev = int(round(ev_beklenti))
    skor_dep = int(round(dep_beklenti))
    skor_tahmin = f"{skor_ev} - {skor_dep}"
    
    # 3. MANTIK ZİNCİRİ (Logic Chain)
    # Skor tahminine göre diğer bahisleri türetiyoruz ki çelişki olmasın.
    
    # KG VAR/YOK
    # Eğer iki takımın da gol beklentisi 0.75'ten büyükse "KG VAR" deriz.
    if ev_beklenti > 0.75 and dep_beklenti > 0.75:
        kg_durum = "VAR"
    else:
        kg_durum = "YOK"
        
    # ALT/ÜST
    toplam_beklenti = ev_beklenti + dep_beklenti
    if toplam_beklenti >= 2.5:
        alt_ust = "2.5 ÜST"
    else:
        alt_ust = "2.5 ALT"
        
    # MAÇ SONUCU
    # İbre hesabı
    ev_guc = ev_beklenti * 100
    dep_guc = dep_beklenti * 100
    fark = ev_guc - dep_guc
    
    ibre = 50 + (fark / 2) # 50 orta nokta
    ibre = max(10, min(90, ibre))
    
    if ibre > 55: ms_tahmin = f"MS 1 ({ev})"
    elif ibre < 45: ms_tahmin = f"MS 2 ({dep})"
    else: ms_tahmin = "MS 0 (Beraberlik)"

    # KORNER (Veri varsa)
    korner = "Veri Yok"
    if 'HC' in df.columns:
        ort_korner = (ev_stats['HC'].mean() + dep_stats['AC'].mean())
        korner = f"{ort_korner:.1f}"
        
    # KART
    kart = "Veri Yok"
    if 'HY' in df.columns:
        ort_kart = (ev_stats['HY'].mean() + ev_stats['AY'].mean() + dep_stats['HY'].mean() + dep_stats['AY'].mean()) / 2
        kart = f"{ort_kart:.1f}"

    return {
        "skor": skor_tahmin,
        "kg": kg_durum,
        "alt_ust": alt_ust,
        "ms": ms_tahmin,
        "ibre": ibre,
        "korner": korner,
        "kart": kart,
        "ev_beklenti": ev_beklenti,
        "dep_beklenti": dep_beklenti,
        "toplam_beklenti": toplam_beklenti
    }

# --- ARAYÜZ ---
st.title("🦁 FUTBOL KAHİNİ MASTER ANALİZ")

# 1. TARİH BİLGİSİ (STATİK DEĞİL, PYTHON İLE BUGÜNÜ ALIR)
bugun = datetime.datetime.now().strftime("%d.%m.%Y")
st.markdown(f"<div style='text-align:center; color:#B0BEC5; margin-bottom:20px;'>📅 Veri Tabanı Tarihi: <span style='color:white; font-weight:bold;'>{bugun}</span> (Güncel Sezon Verileri Kullanılıyor)</div>", unsafe_allow_html=True)

# 2. SEÇİM EKRANI (HATA DÜZELTİLDİ: Session State veya Basit Akış)
col_lig, col_ev, col_dep = st.columns([2, 2, 2])

with col_lig:
    secilen_lig = st.selectbox("LİG SEÇİNİZ", list(lig_kodlari.keys()))

# Ligi seçince veriyi çekiyoruz
df = veri_yukle(secilen_lig)

if df is not None:
    takimlar = sorted(df['HomeTeam'].unique())
    
    with col_ev:
        ev_takim = st.selectbox("EV SAHİBİ", takimlar)
        
    with col_dep:
        # Ev sahibinin aynısını default seçmesin diye index 1
        dep_takim = st.selectbox("DEPLASMAN", takimlar, index=1 if len(takimlar) > 1 else 0)
        
    analiz_btn = st.button("DETAYLI ANALİZİ BAŞLAT 🚀")

    if analiz_btn:
        st.divider()
        res = mantikli_analiz(ev_takim, dep_takim, df)
        
        if res:
            # --- BÖLÜM 1: BÜYÜK SKOR VE GÜVEN ---
            c1, c2 = st.columns([1, 2])
            
            with c1:
                st.markdown(f"""
                <div style="text-align:center; background:#1F2937; padding:20px; border-radius:15px; border:2px solid #00E676;">
                    <div style="color:#B0BEC5; font-size:14px;">YAPAY ZEKA SKOR TAHMİNİ</div>
                    <div style="font-size:48px; font-weight:bold; color:white;">{res['skor']}</div>
                    <div style="color:#00E676; font-size:18px; font-weight:bold;">{res['ms']}</div>
                </div>
                """, unsafe_allow_html=True)
                
            with c2:
                # Gauge Chart
                fig = go.Figure(go.Indicator(
                    mode = "gauge+number",
                    value = res['ibre'],
                    title = {'text': f"{ev_takim} Kazanma Şansı", 'font': {'color': 'white'}},
                    number = {'font': {'color': 'white'}},
                    gauge = {
                        'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "white"},
                        'bar': {'color': "white"},
                        'bgcolor': "#1F2937",
                        'steps': [
                            {'range': [0, 45], 'color': "#FF5252"},
                            {'range': [45, 55], 'color': "gray"},
                            {'range': [55, 100], 'color': "#00E676"}
                        ]
                    }
                ))
                fig.update_layout(height=180, margin=dict(t=30,b=10,l=20,r=20), paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True)

            # --- BÖLÜM 2: DETAYLI BAHİS TABLOSU ---
            st.markdown("### 📋 DETAYLI BAHİS SEÇENEKLERİ")
            
            col_t1, col_t2 = st.columns(2)
            
            with col_t1:
                st.markdown(f"""
                <div class="analiz-card">
                    <div class="bet-row"><span class="bet-title">2.5 GOL BARAJI</span> <span class="bet-val">{res['alt_ust']}</span></div>
                    <div class="bet-row"><span class="bet-title">KG (KARŞILIKLI GOL)</span> <span class="bet-val">{res['kg']}</span></div>
                    <div class="bet-row"><span class="bet-title">TOPLAM GOL BEKLENTİSİ</span> <span class="bet-val">{res['toplam_beklenti']:.2f}</span></div>
                </div>
                """, unsafe_allow_html=True)
                
            with col_t2:
                korner_renk = "bet-val" if res['korner'] != "Veri Yok" and float(res['korner']) > 9.5 else "bet-val-risk"
                kart_renk = "bet-val-risk" if res['kart'] != "Veri Yok" and float(res['kart']) > 4.5 else "bet-val"
                
                st.markdown(f"""
                <div class="analiz-card">
                    <div class="bet-row"><span class="bet-title">KORNER TAHMİNİ</span> <span class="{korner_renk}">{res['korner']}</span></div>
                    <div class="bet-row"><span class="bet-title">KART / SERTLİK PUANI</span> <span class="{kart_renk}">{res['kart']}</span></div>
                    <div class="bet-row"><span class="bet-title">MAÇIN RİSK DURUMU</span> <span class="bet-val" style="color:yellow !important;">{'YÜKSEK' if 45 < res['ibre'] < 55 else 'NORMAL'}</span></div>
                </div>
                """, unsafe_allow_html=True)

            # --- BÖLÜM 3: GRAFİKLİ ANLATIM (AÇIKLAMALI) ---
            st.markdown("### 📊 GRAFİKSEL ANALİZ & YORUM")
            
            g1, g2 = st.columns([2, 1])
            
            with g1:
                # Çubuk Grafik (Hücum Gücü)
                fig_bar = go.Figure(data=[
                    go.Bar(name='Ev Sahibi', x=['Gol Beklentisi'], y=[res['ev_beklenti']], marker_color='#00E676'),
                    go.Bar(name='Deplasman', x=['Gol Beklentisi'], y=[res['dep_beklenti']], marker_color='#FF5252')
                ])
                fig_bar.update_layout(
                    title="Takımların Gol Potansiyeli",
                    paper_bgcolor='rgba(0,0,0,0)', 
                    plot_bgcolor='rgba(0,0,0,0)',
                    font={'color': 'white'},
                    barmode='group',
                    height=250
                )
                st.plotly_chart(fig_bar, use_container_width=True)
                
            with g2:
                st.info("💡 **GRAFİK NE ANLATIYOR?**")
                st.markdown(f"""
                Bu grafik takımların **Gol Beklentisi (xG)** verilerini karşılaştırır.
                
                * **Yeşil Çubuk ({ev_takim}):** Maç başına {res['ev_beklenti']:.2f} gol atması bekleniyor.
                * **Kırmızı Çubuk ({dep_takim}):** Maç başına {res['dep_beklenti']:.2f} gol atması bekleniyor.
                
                *Eğer çubuklar 1.5 üzerindeyse bol gollü bir maç izleriz.*
                """)

        else:
            st.error("Bu takımlar için yeterli veri bulunamadı (Sezon başı olabilir).")
