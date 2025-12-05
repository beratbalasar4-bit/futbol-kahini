import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# --- SAYFA AYARLARI (Full Screen) ---
st.set_page_config(page_title="AI Futbol Asistanı", page_icon="🧠", layout="wide")

# --- MODERN CSS TASARIMI ---
st.markdown("""
<style>
    .stApp { background-color: #0E1117; }
    h1, h2, h3 { color: #00CC96 !important; font-family: 'Helvetica Neue', sans-serif; }
    .metric-card { background-color: #262730; padding: 15px; border-radius: 10px; border-left: 5px solid #00CC96; }
    div[data-testid="stMetricValue"] { font-size: 24px; color: white; }
</style>
""", unsafe_allow_html=True)

# --- İSİM DÜZELTME ---
takim_duzeltme = {
    "Fenerbahce": "Fenerbahçe", "Galatasaray": "Galatasaray", "Besiktas": "Beşiktaş",
    "Trabzonspor": "Trabzonspor", "Buyuksehyr": "Başakşehir FK", "Man City": "Manchester City",
    "Man United": "Manchester United", "Liverpool": "Liverpool", "Arsenal": "Arsenal"
}

# --- VERİ ÇEKME ---
@st.cache_data(ttl=3600)
def veri_getir(lig_kodu):
    url = "https://www.football-data.co.uk/mmz4281/2425/T1.csv" if lig_kodu == "TR" else "https://www.football-data.co.uk/mmz4281/2425/E0.csv"
    try:
        df = pd.read_csv(url)
        df = df.dropna(subset=['FTR'])
        df['HomeTeam'] = df['HomeTeam'].replace(takim_duzeltme)
        df['AwayTeam'] = df['AwayTeam'].replace(takim_duzeltme)
        return df
    except: return None

# --- BAŞLIK ---
col_logo, col_title = st.columns([1, 5])
with col_logo:
    st.markdown("# 🧠")
with col_title:
    st.title("FUTBOL ASİSTANI")
    st.caption("Yapay Zeka Destekli Maç Önü Analiz Platformu")

st.divider()

# --- YAN MENÜ ---
with st.sidebar:
    st.header("⚙️ Maç Seçimi")
    lig = st.selectbox("Lig Seç:", ("Türkiye Süper Lig", "İngiltere Premier Lig"))
    df = veri_getir("TR" if lig == "Türkiye Süper Lig" else "EN")
    
    if df is not None:
        takimlar = sorted(df['HomeTeam'].unique())
        ev = st.selectbox("Ev Sahibi", takimlar)
        dep = st.selectbox("Deplasman", takimlar, index=1)
        analiz_btn = st.button("ANALİZİ BAŞLAT ➤", type="primary")
    else:
        st.error("Veri Sunucusu Hatası")

# --- ANA EKRAN ---
if df is not None and analiz_btn:
    # İSTATİSTİK MOTORU
    ev_stats = df[df['HomeTeam'] == ev]
    dep_stats = df[df['AwayTeam'] == dep]

    if len(ev_stats) > 0 and len(dep_stats) > 0:
        # 1. GÜÇ HESAPLAMA
        # Gol atma ve yeme istatistiklerinden "Saldırı" ve "Defans" puanı (0-100 arası) çıkarıyoruz
        ev_att = min(100, (ev_stats['FTHG'].mean() * 30) + 20)
        ev_def = min(100, 100 - (ev_stats['FTAG'].mean() * 30))
        
        dep_att = min(100, (dep_stats['FTAG'].mean() * 30) + 20)
        dep_def = min(100, 100 - (dep_stats['FTHG'].mean() * 30))

        # 2. RADAR GRAFİĞİ (FIFA TARZI)
        categories = ['Hücum Gücü', 'Defans Gücü', 'Şut İsabeti', 'Form Durumu', 'Gol Beklentisi']
        
        # Basit formülle diğer değerleri üretiyoruz (Gerçek projede daha detaylı formül kullanırız)
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=[ev_att, ev_def, ev_att-10, ev_att+5, ev_att-5],
            theta=categories,
            fill='toself',
            name=ev,
            line_color='#00CC96'
        ))
        fig.add_trace(go.Scatterpolar(
            r=[dep_att, dep_def, dep_att-5, dep_att-10, dep_att+5],
            theta=categories,
            fill='toself',
            name=dep,
            line_color='#FF4B4B'
        ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=True,
            title="Takım Güç Karşılaştırması",
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )

        # 3. KAHİN GÖSTERGESİ (RİSK BAROMETRESİ)
        # Fark hesapla
        fark = (ev_att + ev_def) - (dep_att + dep_def)
        if fark > 10: ibre_degeri = 80 # Ev sahibi favori
        elif fark < -10: ibre_degeri = 20 # Deplasman favori
        else: ibre_degeri = 50 # Ortada

        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = ibre_degeri,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "AI Galibiyet İbresi"},
            gauge = {
                'axis': {'range': [0, 100]},
                'bar': {'color': "white"},
                'steps': [
                    {'range': [0, 40], 'color': "#FF4B4B"}, # Kırmızı (Dep)
                    {'range': [40, 60], 'color': "gray"},   # Gri (Beraberlik)
                    {'range': [60, 100], 'color': "#00CC96"}], # Yeşil (Ev)
            }
        ))
        fig_gauge.update_layout(height=300, margin=dict(l=20,r=20,t=50,b=20), paper_bgcolor='rgba(0,0,0,0)')

        # --- EKRANA YERLEŞTİRME (Dashboard Düzeni) ---
        
        # Üst Kısım: Skor Tahmini
        c1, c2, c3 = st.columns([1,2,1])
        with c2:
            st.info(f"🤖 **Yapay Zeka Tahmini:** {(ev_att/40):.1f} - {(dep_att/40):.1f}")

        # Orta Kısım: Grafikler
        left_col, right_col = st.columns(2)
        with left_col:
            st.plotly_chart(fig, use_container_width=True)
        with right_col:
            st.plotly_chart(fig_gauge, use_container_width=True)
            
            # Altına Yorum
            if ibre_degeri > 60:
                st.success(f"Bu maçta ibre **{ev}** tarafını gösteriyor. Ev sahibi avantajlı.")
            elif ibre_degeri < 40:
                st.error(f"Bu maçta ibre **{dep}** tarafını gösteriyor. Sürpriz çıkabilir!")
            else:
                st.warning("İbre tam ortada! Çok riskli maç, uzak durulması önerilir.")

        # Alt Kısım: Detaylı İstatistikler (Tablo)
        st.subheader("📊 Kritik Veriler")
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Ev Gol Ort.", f"{ev_stats['FTHG'].mean():.2f}")
        k2.metric("Dep Gol Ort.", f"{dep_stats['FTAG'].mean():.2f}")
        k3.metric("Ev Şut Gücü", f"{ev_stats['HST'].mean():.1f}")
        k4.metric("Dep Şut Gücü", f"{dep_stats['AST'].mean():.1f}")

    else:
        st.warning("Bu takımlar için henüz yeterli veri oluşmamış.")

else:
    # Açılış Ekranı (Kullanıcı henüz butona basmadı)
    st.markdown("""
    <div style='text-align: center; padding: 50px;'>
        <h3>👈 Soldaki menüden lig ve takımları seçip analizi başlat!</h3>
        <p style='color: gray;'>Veriler İngiltere Premier Lig ve Türkiye Süper Lig sunucularından anlık çekilir.</p>
    </div>
    """, unsafe_allow_html=True)
