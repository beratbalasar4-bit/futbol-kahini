import streamlit as st
import pandas as pd

# --- SAYFA AYARLARI (Geniş Mod) ---
st.set_page_config(page_title="Futbol Kahini Pro", page_icon="⚽", layout="wide")

# --- CSS İLE GÖRSEL DÜZENLEME ---
st.markdown("""
<style>
    .big-font { font-size:20px !important; font-weight: bold; }
    .metric-box { border: 1px solid #333; padding: 10px; border-radius: 10px; text-align: center; }
</style>
""", unsafe_allow_html=True)

# --- 1. İSİM DÜZELTME SÖZLÜĞÜ ---
# İngilizlerin yazdığı bozuk isimleri düzeltiyoruz
takim_duzeltme = {
    "Fenerbahce": "Fenerbahçe",
    "Galatasaray": "Galatasaray",
    "Besiktas": "Beşiktaş",
    "Trabzonspor": "Trabzonspor",
    "Buyuksehyr": "Başakşehir FK",
    "Ankaragucu": "Ankaragücü",
    "Karagumruk": "Fatih Karagümrük",
    "Alanyaspor": "Alanyaspor",
    "Antalyaspor": "Antalyaspor",
    "Sivasspor": "Sivasspor",
    "Konyaspor": "Konyaspor",
    "Kasimpasa": "Kasımpaşa",
    "Gaziantep": "Gaziantep FK",
    "Hatayspor": "Hatayspor",
    "Rizespor": "Çaykur Rizespor",
    "Samsunspor": "Samsunspor",
    "Pendikspor": "Pendikspor",
    "Istanbulspor": "İstanbulspor",
    "Adana Demir": "Adana Demirspor",
    "Man City": "Manchester City",
    "Man United": "Manchester United",
    "Liverpool": "Liverpool",
    "Arsenal": "Arsenal",
    "Chelsea": "Chelsea",
    "Tottenham": "Tottenham"
}

# --- 2. LOGO GETİRME FONKSİYONU ---
def logo_getir(takim_adi):
    # Logoların internet adresleri (Örnek olarak büyükleri ekledim)
    logolar = {
        "Fenerbahçe": "https://upload.wikimedia.org/wikipedia/tr/8/86/Fenerbah%C3%A7e_SK.png",
        "Galatasaray": "https://upload.wikimedia.org/wikipedia/commons/f/f6/Galatasaray_Sports_Club_Logo.png",
        "Beşiktaş": "https://upload.wikimedia.org/wikipedia/commons/2/20/Besiktas_jk.png",
        "Trabzonspor": "https://upload.wikimedia.org/wikipedia/tr/a/ab/Trabzonspor_Amblem.png",
        "Manchester City": "https://upload.wikimedia.org/wikipedia/tr/f/f6/Manchester_City.png",
        "Liverpool": "https://upload.wikimedia.org/wikipedia/tr/3/3f/Liverpool_FC_logo.png",
        "Arsenal": "https://upload.wikimedia.org/wikipedia/tr/5/53/Arsenal_FC.svg",
        "Manchester United": "https://upload.wikimedia.org/wikipedia/tr/b/b6/Manchester_United_FC_logo.png"
    }
    return logolar.get(takim_adi, "https://cdn-icons-png.flaticon.com/512/53/53283.png") # Bulamazsa top resmi koy

# --- 3. VERİ ÇEKME ---
@st.cache_data(ttl=3600)
def veri_getir(lig_kodu):
    url = ""
    if lig_kodu == "TR": url = "https://www.football-data.co.uk/mmz4281/2425/T1.csv"
    elif lig_kodu == "EN": url = "https://www.football-data.co.uk/mmz4281/2425/E0.csv"
    
    try:
        df = pd.read_csv(url)
        df = df.dropna(subset=['FTR'])
        # İsimleri Türkçeye çevir (Replace komutu)
        df['HomeTeam'] = df['HomeTeam'].replace(takim_duzeltme)
        df['AwayTeam'] = df['AwayTeam'].replace(takim_duzeltme)
        return df
    except:
        return None

# --- ARAYÜZ ---
st.title("🦁 FUTBOL KÂHİNİ PRO")
st.markdown("---")

# Yan Menü
with st.sidebar:
    st.header("⚙️ Ayarlar")
    lig_secimi = st.selectbox("Lig Seçiniz:", ("Türkiye Süper Lig", "İngiltere Premier Lig"))
    st.info("Veriler İngiltere sunucularından anlık çekilmektedir.")

# Veriyi Yükle
if lig_secimi == "Türkiye Süper Lig":
    df = veri_getir("TR")
else:
    df = veri_getir("EN")

if df is not None:
    takimlar = sorted(df['HomeTeam'].unique())
    
    # --- TAKIM SEÇİM ALANI (YAN YANA) ---
    col1, col2, col3 = st.columns([1, 0.2, 1])
    
    with col1:
        ev_sahibi = st.selectbox("Ev Sahibi", takimlar)
        st.image(logo_getir(ev_sahibi), width=100)
        
    with col2:
        st.markdown("<h1 style='text-align: center; padding-top: 50px;'>VS</h1>", unsafe_allow_html=True)
        
    with col3:
        deplasman = st.selectbox("Deplasman", takimlar, index=1)
        st.image(logo_getir(deplasman), width=100)

    # --- ANALİZ SEKME YAPISI ---
    tab1, tab2 = st.tabs(["📊 DETAYLI ANALİZ", "📝 FORM DURUMU"])

    with tab1:
        if st.button("MAÇI ANALİZ ET 🚀", type="primary", use_container_width=True):
            # İstatistik Hesapla
            ev_stats = df[df['HomeTeam'] == ev_sahibi]
            dep_stats = df[df['AwayTeam'] == deplasman]
            
            if len(ev_stats) > 0 and len(dep_stats) > 0:
                ev_gol = ev_stats['FTHG'].mean()
                dep_gol = dep_stats['FTAG'].mean()
                ev_sut = ev_stats['HST'].mean() if 'HST' in df.columns else 4.5
                dep_sut = dep_stats['AST'].mean() if 'AST' in df.columns else 4.0
                
                # Tahmin
                ev_beklenen = (ev_gol + dep_gol + (ev_sut/5)) / 2.05
                dep_beklenen = (dep_gol + ev_gol + (dep_sut/5)) / 2.3
                
                fark = ev_beklenen - dep_beklenen
                
                # --- SONUÇ KARTLARI ---
                c1, c2, c3 = st.columns(3)
                c1.metric(label=f"{ev_sahibi} Gol Beklentisi", value=f"{ev_beklenen:.2f}")
                c2.metric(label="Tahmini Fark", value=f"{fark:.2f}")
                c3.metric(label=f"{deplasman} Gol Beklentisi", value=f"{dep_beklenen:.2f}")
                
                st.divider()
                
                # Yorum
                if fark > 0.4:
                    st.success(f"🏆 **TAHMİN:** {ev_sahibi} sahasında avantajlı! (MS 1)")
                elif fark < -0.4:
                    st.error(f"🏆 **TAHMİN:** {deplasman} deplasmanda sürpriz yapabilir! (MS 2)")
                else:
                    st.warning("⚖️ **TAHMİN:** Maç ortada. Beraberlik yüksek ihtimal.")
                    
                # Gol Yorumu
                toplam = ev_beklenen + dep_beklenen
                if toplam > 2.55:
                    st.info(f"⚽ **GOL:** Maç hareketli geçer. ({toplam:.1f} Gol Beklentisi -> 2.5 ÜST)")
                else:
                    st.info(f"🧊 **GOL:** Maç kontrollü geçer. ({toplam:.1f} Gol Beklentisi -> 2.5 ALT)")
            else:
                st.warning("Henüz yeterli veri yok (Sezon başı olabilir).")

    with tab2:
        st.subheader("Son Oynanan Maçlar")
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.write(f"**{ev_sahibi} (Evinde)**")
            son_maclar_ev = df[df['HomeTeam'] == ev_sahibi].tail(5)
            st.dataframe(son_maclar_ev[['AwayTeam', 'FTHG', 'FTAG', 'FTR']], hide_index=True)
            
        with col_b:
            st.write(f"**{deplasman} (Deplasmanda)**")
            son_maclar_dep = df[df['AwayTeam'] == deplasman].tail(5)
            st.dataframe(son_maclar_dep[['HomeTeam', 'FTHG', 'FTAG', 'FTR']], hide_index=True)

else:
    st.error("Veri alınamadı.")
