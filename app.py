import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Moodist: Duygu Haritası", page_icon="✨", layout="wide")

# --- CSS (MODERN TASARIM) ---
st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: #E0E0E0; }
    h1 { color: #FF4B4B; font-family: 'Helvetica', sans-serif; font-weight: 800; }
    .mood-card {
        background-color: #1E1E1E; padding: 20px; border-radius: 15px;
        border: 1px solid #333; text-align: center; margin-bottom: 10px;
        transition: transform 0.2s;
    }
    .mood-card:hover { transform: scale(1.05); border-color: #FF4B4B; }
    .tag {
        background-color: #FF4B4B; color: white; padding: 2px 8px; 
        border-radius: 10px; font-size: 12px; margin-right: 5px;
    }
</style>
""", unsafe_allow_html=True)

# --- 1. VERİTABANI (SİMÜLASYON) ---
# Normalde burası Google Maps API'den ve Yapay Zeka analizinden gelecek.
# Şimdilik "Muğla/İstanbul" karışık örnek verilerle dolduruyorum.

MEKAN_VERITABANI = [
    {
        "isim": "Kütüphane Kafe", "konum": [41.0422, 29.0067], "ilce": "Beşiktaş",
        "yorum_ozeti": "İçerisi çıt çıkmıyor, herkes bilgisayar başında.",
        "moods": ["Ders Çalış", "Kafa Dinle", "Sessiz"],
        "puan": 4.8, "fiyat": "₺"
    },
    {
        "isim": "Dark Blue Jazz Club", "konum": [41.0256, 28.9741], "ilce": "Galata",
        "yorum_ozeti": "Loş ışıklar, hafif müzik, tam sevgilini getirmelik.",
        "moods": ["Romantik", "Date Night", "Loş"],
        "puan": 4.5, "fiyat": "₺₺₺"
    },
    {
        "isim": "Dedikodu Kahvesi", "konum": [40.9906, 29.0238], "ilce": "Kadıköy",
        "yorum_ozeti": "Müzik sesi düşük, masalar arası mesafe iyi, saatlerce konuşmalık.",
        "moods": ["Dedikodu", "Arkadaşlarla", "Konforlu"],
        "puan": 4.2, "fiyat": "₺₺"
    },
    {
        "isim": "Ayrılık Sonrası Teras", "konum": [41.0369, 28.9850], "ilce": "Taksim",
        "yorum_ozeti": "Manzaraya karşı ağlamak serbest, kimse karışmıyor.",
        "moods": ["Melankolik", "Yalnızlık", "Manzara"],
        "puan": 4.6, "fiyat": "₺₺"
    },
    {
        "isim": "Enerji Patlaması Gym & Bar", "konum": [41.0683, 29.0113], "ilce": "Etiler",
        "yorum_ozeti": "Müzik çok yüksek, yerinde duramıyorsun.",
        "moods": ["Eğlence", "Yüksek Enerji", "Party"],
        "puan": 4.1, "fiyat": "₺₺₺₺"
    },
    # Muğla Örneği (Senin için)
    {
        "isim": "Akyaka Kitap Evi", "konum": [37.0534, 28.3236], "ilce": "Muğla/Akyaka",
        "yorum_ozeti": "Dere kenarında, sadece su sesi var.",
        "moods": ["Kafa Dinle", "Huzur", "Sessiz"],
        "puan": 4.9, "fiyat": "₺₺"
    }
]

# DataFrame'e çevir
df = pd.DataFrame(MEKAN_VERITABANI)

# --- 2. FONKSİYONLAR ---

def harita_olustur(filtrelenmis_df):
    # Harita merkezini (Ortalama konum) ayarla
    if not filtrelenmis_df.empty:
        merkez = [filtrelenmis_df['konum'].apply(lambda x: x[0]).mean(), 
                  filtrelenmis_df['konum'].apply(lambda x: x[1]).mean()]
    else:
        merkez = [41.0082, 28.9784] # İstanbul

    m = folium.Map(location=merkez, zoom_start=11, tiles="CartoDB dark_matter")

    for _, row in filtrelenmis_df.iterrows():
        # Mood'a göre ikon rengi
        renk = "red"
        if "Huzur" in row['moods'] or "Sessiz" in row['moods']: renk = "green"
        if "Romantik" in row['moods']: renk = "purple"
        if "Eğlence" in row['moods']: renk = "orange"

        html_content = f"""
        <div style="font-family:sans-serif; width:200px;">
            <h4 style="margin:0;">{row['isim']}</h4>
            <p style="font-size:11px; color:gray;">{row['ilce']} | {row['fiyat']}</p>
            <p style="font-size:12px;"><i>"{row['yorum_ozeti']}"</i></p>
            <b style="color:{renk}">{', '.join(row['moods'])}</b>
        </div>
        """
        
        folium.Marker(
            location=row['konum'],
            popup=folium.Popup(html_content, max_width=250),
            icon=folium.Icon(color=renk, icon="info-sign"),
            tooltip=row['isim']
        ).add_to(m)
        
    return m

# --- 3. ARAYÜZ ---

c1, c2 = st.columns([1, 4])

with c1:
    st.title("Moodist")
    st.caption("Mekanları değil, hisleri keşfet.")
    st.divider()
    
    # MOOD SEÇİCİ
    st.subheader("Bugün modun ne?")
    mood_secimi = st.radio(
        "Birini Seç:",
        ["Hepsi", "Kafa Dinle 🧘", "Ders Çalış 📚", "Romantik ❤️", "Dedikodu ☕", "Eğlence 🔥", "Melankolik 🌧️"]
    )
    
    st.info("💡 **Nasıl Çalışır?**\nYapay zeka, binlerce Google yorumunu okur ve mekanın 'ruhunu' analiz eder.")

with c2:
    # FİLTRELEME MANTIĞI
    if mood_secimi == "Hepsi":
        df_filtered = df
    else:
        # Seçilen mood'un anahtar kelimesini al (Örn: "Kafa Dinle 🧘" -> "Kafa Dinle")
        anahtar = mood_secimi.split(" ")[0] 
        # Veritabanında mood listesinde bu kelime geçiyor mu bak
        df_filtered = df[df['moods'].apply(lambda x: any(anahtar in s for s in x))]

    # HARİTA
    st_map = harita_olustur(df_filtered)
    st_folium(st_map, width="100%", height=500)
    
    # LİSTE GÖRÜNÜMÜ
    st.subheader(f"📍 Senin Moduna Uygun {len(df_filtered)} Mekan Bulundu")
    
    if not df_filtered.empty:
        cols = st.columns(3)
        for idx, row in df_filtered.iterrows():
            with cols[idx % 3]:
                st.markdown(f"""
                <div class="mood-card">
                    <h3>{row['isim']}</h3>
                    <p style="color:#aaa; font-size:12px;">{row['ilce']} • {row['fiyat']} • ⭐{row['puan']}</p>
                    <p style="font-style:italic; font-size:13px;">"{row['yorum_ozeti']}"</p>
                    <div>
                        {' '.join([f'<span class="tag">{m}</span>' for m in row['moods']])}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.warning("Bu modda henüz keşfedilmiş bir mekan yok. Başka bir mod dene!")
