import streamlit as st
import pandas as pd

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Futbol Kahini", page_icon="⚽")

# --- BAŞLIK VE GÖRSEL ---
st.title("🦁 FUTBOL KÂHİNİ (AI)")
st.write("Türkiye Süper Lig ve İngiltere Premier Lig Yapay Zeka Analizi")

# --- 1. OTOMATİK VERİ ÇEKME MOTORU (CANLI) ---
@st.cache_data(ttl=3600) # Veriyi 1 saat önbellekte tut (Hız için)
def veri_getir(lig_kodu):
    # 2425 = 2024/2025 Sezonu demektir. Seneye burayı 2526 yaparız.
    url = ""
    if lig_kodu == "TR":
        url = "https://www.football-data.co.uk/mmz4281/2425/T1.csv"
    elif lig_kodu == "EN":
        url = "https://www.football-data.co.uk/mmz4281/2425/E0.csv"
    
    try:
        df = pd.read_csv(url)
        df = df.dropna(subset=['FTR']) # Oynanmamış maçları temizle
        return df
    except:
        return None

# --- 2. YAN MENÜ (LİG SEÇİMİ) ---
lig_secimi = st.sidebar.selectbox("Hangi Ligi Analiz Edelim?", ("Türkiye Süper Lig", "İngiltere Premier Lig"))

if lig_secimi == "Türkiye Süper Lig":
    df = veri_getir("TR")
    st.sidebar.success("🇹🇷 Süper Lig Verileri Canlı Çekildi!")
else:
    df = veri_getir("EN")
    st.sidebar.success("🇬🇧 Premier Lig Verileri Canlı Çekildi!")

if df is not None:
    takimlar = sorted(df['HomeTeam'].unique())
    
    # --- 3. TAKIM SEÇİM EKRANI ---
    col1, col2 = st.columns(2)
    with col1:
        ev_sahibi = st.selectbox("Ev Sahibi Takım", takimlar)
    with col2:
        deplasman = st.selectbox("Deplasman Takım", takimlar, index=1)

    # --- 4. ANALİZ BUTONU ---
    if st.button("MAÇI ANALİZ ET 🚀", type="primary"):
        # İstatistikleri Hesapla
        ev_stats = df[df['HomeTeam'] == ev_sahibi]
        dep_stats = df[df['AwayTeam'] == deplasman]

        if len(ev_stats) > 0 and len(dep_stats) > 0:
            # Güç Hesaplamaları
            ev_gol = ev_stats['FTHG'].mean()
            ev_defans = ev_stats['FTAG'].mean()
            ev_sut = ev_stats['HST'].mean() if 'HST' in df.columns else 5.0 # Veri yoksa varsayılan

            dep_gol = dep_stats['FTAG'].mean()
            dep_defans = dep_stats['FTHG'].mean()
            dep_sut = dep_stats['AST'].mean() if 'AST' in df.columns else 5.0

            # Tahmin Formülü
            ev_beklenen = (ev_gol + dep_defans + (ev_sut/5)) / 2.1
            dep_beklenen = (dep_gol + ev_defans + (dep_sut/5)) / 2.1

            skor_farki = ev_beklenen - dep_beklenen
            toplam_gol = ev_beklenen + dep_beklenen

            # Sonuçları Göster
            st.divider()
            st.subheader(f"📊 {ev_sahibi} vs {deplasman}")
            
            # Skor Tahmini (Büyük Puntolarla)
            c1, c2 = st.columns(2)
            c1.metric("Ev Sahibi Beklenti", f"{ev_beklenen:.2f}")
            c2.metric("Deplasman Beklenti", f"{dep_beklenen:.2f}")

            # Yorum
            st.info(f"🧠 **Yapay Zeka Yorumu:**")
            
            if skor_farki > 0.4:
                st.success(f"🏆 **{ev_sahibi}** galibiyete çok yakın! (MS 1)")
            elif skor_farki < -0.4:
                st.error(f"🏆 **{deplasman}** galibiyete çok yakın! (MS 2)")
            else:
                st.warning("💣 Maç ortada görünüyor, beraberlik riski yüksek.")

            if toplam_gol > 2.6:
                st.write("🔥 **Gol Tahmini:** Maçın 2.5 ÜST bitme ihtimali yüksek.")
            else:
                st.write("🧊 **Gol Tahmini:** Maçın kısır geçmesi bekleniyor (2.5 ALT).")

        else:
            st.error("Bu takımların yeterli verisi henüz oluşmamış.")

else:
    st.error("Veri sunucusuna bağlanılamadı. Lütfen sonra tekrar dene.")
