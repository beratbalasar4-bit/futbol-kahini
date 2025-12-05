import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.graph_objects as go
import time
import random

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Futbol Kahini SuperApp", page_icon="🦁", layout="wide")

# --- TASARIM VE CSS ---
st.markdown("""
<style>
    .stApp { background-color: #0E1117; }
    h1 { color: #00CC96 !important; text-align: center; font-family: 'Arial Black', sans-serif; }
    
    /* Form Kutucukları */
    .form-box { display: inline-block; width: 30px; height: 30px; margin: 2px; text-align: center; line-height: 30px; color: white; border-radius: 5px; font-weight: bold; font-size: 14px; }
    .win { background-color: #2ECC71; }
    .draw { background-color: #95A5A6; }
    .loss { background-color: #E74C3C; }

    /* Kupon Kartı */
    .kupon-karti { background-color: #1F2937; padding: 20px; border-radius: 15px; border-left: 8px solid #00CC96; margin-bottom: 15px; }
    
    .stButton>button { 
        background: linear-gradient(to right, #00CC96, #00b887); 
        color: white; width: 100%; border-radius: 10px; height: 50px; border: none; font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --- YAN MENÜ ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3233/3233496.png", width=100)
    st.markdown("### 🦁 SÜPER ASİSTAN")
    st.info("Bu sürümde Form Analizi, Otomatik Kupon ve Sohbet Robotu bir arada!")
    st.markdown("---")
    st.link_button("👉 Telegram Grubumuz", "https://t.me/ornek_link")

st.title("🌍 FUTBOL KAHİNİ SÜPER APP")

# --- VERİ MOTORU ---
lig_kodlari = {
    "🇹🇷 Türkiye Süper Lig": "T1.csv",
    "🇬🇧 İngiltere Premier Lig": "E0.csv",
    "🇪🇸 İspanya La Liga": "SP1.csv",
    "🇩🇪 Almanya Bundesliga": "D1.csv",
    "🇮🇹 İtalya Serie A": "I1.csv",
    "🇫🇷 Fransa Ligue 1": "F1.csv"
}

takim_duzeltme = {
    "Fenerbahce": "Fenerbahçe", "Galatasaray": "Galatasaray", "Besiktas": "Beşiktaş", "Trabzonspor": "Trabzonspor",
    "Buyuksehyr": "Başakşehir FK", "Man City": "Manchester City", "Man United": "Manchester United",
    "Real Madrid": "Real Madrid", "Barcelona": "Barcelona", "Bayern Munich": "Bayern Münih",
    "Paris SG": "PSG", "Inter": "Inter Milan", "Milan": "AC Milan", "Juventus": "Juventus"
}

@st.cache_data(ttl=3600)
def veri_getir(secilen_lig):
    dosya_adi = lig_kodlari[secilen_lig]
    ana_url = "https://www.football-data.co.uk/mmz4281/2425/"
    full_url = ana_url + dosya_adi
    try:
        df = pd.read_csv(full_url)
        df = df.dropna(subset=['FTR'])
        df['HomeTeam'] = df['HomeTeam'].replace(takim_duzeltme)
        df['AwayTeam'] = df['AwayTeam'].replace(takim_duzeltme)
        return df
    except: return None

# --- YARDIMCI: FORM HESAPLAMA (SON 5 MAÇ) ---
def form_getir(takim, df):
    # Takımın oynadığı son 5 maçı bul
    maclar = df[(df['HomeTeam'] == takim) | (df['AwayTeam'] == takim)].tail(5)
    html_kod = ""
    
    for index, row in maclar.iterrows():
        sonuc = "B"
        renk = "draw"
        
        if row['HomeTeam'] == takim:
            if row['FTR'] == 'H': sonuc, renk = "G", "win"
            elif row['FTR'] == 'A': sonuc, renk = "M", "loss"
        else: # Deplasman
            if row['FTR'] == 'A': sonuc, renk = "G", "win"
            elif row['FTR'] == 'H': sonuc, renk = "M", "loss"
            
        html_kod += f"<div class='form-box {renk}'>{sonuc}</div>"
    
    return html_kod if html_kod else "<span style='color:gray'>Veri Yok</span>"

# --- ANA SEKME YAPISI ---
tab1, tab2, tab3 = st.tabs(["📊 DETAYLI ANALİZ", "🎰 OTOMATİK KUPON", "🤖 AI SOHBET"])

# ================= SEKME 1: ANALİZ & FORM =================
with tab1:
    col_lig = st.selectbox("Lig Seçiniz:", list(lig_kodlari.keys()), key="lig1")
    df = veri_getir(col_lig)

    if df is not None:
        takimlar = sorted(df['HomeTeam'].unique())
        c1, c2 = st.columns(2)
        with c1: ev = st.selectbox("Ev Sahibi", takimlar)
        with c2: dep = st.selectbox("Deplasman", takimlar, index=1)

        # FORM DURUMU GÖSTERGESİ (YENİ!)
        st.markdown("### 📈 SON 5 MAÇ FORMU")
        f1, f2 = st.columns(2)
        with f1: 
            st.markdown(f"**{ev}**")
            st.markdown(form_getir(ev, df), unsafe_allow_html=True)
        with f2: 
            st.markdown(f"**{dep}**")
            st.markdown(form_getir(dep, df), unsafe_allow_html=True)
        
        st.write("")
        if st.button("MAÇI ANALİZ ET 🚀"):
            ev_stats = df[df['HomeTeam'] == ev]
            dep_stats = df[df['AwayTeam'] == dep]
            
            if len(ev_stats) > 0:
                # Hesaplamalar
                ev_guc = (ev_stats['FTHG'].mean() * 40) + 10
                dep_guc = (dep_stats['FTAG'].mean() * 40) + 10
                fark = ev_guc - dep_guc
                ibre = 50 + (fark / 1.5)
                ibre = max(10, min(90, ibre))
                
                # İbre
                fig_gauge = go.Figure(go.Indicator(
                    mode = "gauge+number", value = ibre,
                    title = {'text': "Ev Sahibi Şansı %"},
                    gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': "white"}, 'steps': [{'range': [0, 45], 'color': "#FF4B4B"}, {'range': [55, 100], 'color': "#00CC96"}]}
                ))
                fig_gauge.update_layout(height=250, margin=dict(t=30,b=20,l=20,r=20), paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_gauge, use_container_width=True)
                
                # Yorum
                if ibre > 60: st.success(f"🔥 **{ev}** favori görünüyor!")
                elif ibre < 40: st.error(f"⚠️ **{dep}** sürpriz yapabilir!")
                else: st.warning("⚖️ Maç ortada görünüyor.")

# ================= SEKME 2: OTOMATİK KUPON =================
with tab2:
    st.subheader("🤖 YAPAY ZEKA GÜNÜN KUPONU")
    st.info("Yapay zeka seçilen ligdeki en güçlü ev sahiplerini tarar.")
    
    lig_oto = st.selectbox("Hangi ligden kupon yapalım?", list(lig_kodlari.keys()), key="lig2")
    
    if st.button("BANKO KUPON YARAT 🎰"):
        df_oto = veri_getir(lig_oto)
        if df_oto is not None:
            with st.spinner("Maçlar taranıyor..."):
                time.sleep(1)
                # Basit Algoritma: En çok gol atan ev sahipleri
                takimlar = df_oto['HomeTeam'].unique()
                liste = []
                for t in takimlar:
                    s = df_oto[df_oto['HomeTeam'] == t]
                    if len(s) > 0:
                        puan = s['FTHG'].mean() * 2 - s['FTAG'].mean()
                        liste.append({"Takım": t, "Puan": puan})
                
                en_iyiler = sorted(liste, key=lambda x: x['Puan'], reverse=True)[:3]
                
                for mac in en_iyiler:
                    st.markdown(f"""
                    <div class="kupon-karti">
                        <h3 style="color:#00CC96; margin:0;">{mac['Takım']}</h3>
                        <p style="color:white;">Yapay Zeka Güven Skoru: <b>{mac['Puan']:.2f}</b></p>
                        <small style="color:gray;">Tahmin: Maç Sonucu 1</small>
                    </div>
                    """, unsafe_allow_html=True)

# ================= SEKME 3: AI SOHBET (CHATBOT) =================
with tab3:
    st.subheader("💬 FUTBOL ASİSTANI İLE SOHBET ET")
    st.caption("Takımlar hakkında sorular sorabilirsin. (Örn: 'Galatasaray gol durumu', 'Fener formda mı?')")

    # Chat Geçmişi
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Merhaba! Hangi takımı merak ediyorsun?"}]

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Kullanıcı Girişi
    if prompt := st.chat_input("Sorunu yaz..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        # --- BASİT CEVAP MOTORU ---
        cevap = "Bunu tam anlayamadım, daha basit sorar mısın?"
        prompt_lower = prompt.lower()
        
        # Seçili ligdeki veriyi kullan
        df_chat = veri_getir(col_lig) 
        if df_chat is not None:
            takimlar = df_chat['HomeTeam'].unique()
            bulunan_takim = None
            
            # Mesajda takım ismi ara
            for t in takimlar:
                if t.lower() in prompt_lower:
                    bulunan_takim = t
                    break
            
            if bulunan_takim:
                stats = df_chat[df_chat['HomeTeam'] == bulunan_takim]
                gol_ort = stats['FTHG'].mean()
                if "gol" in prompt_lower:
                    cevap = f"⚽ **{bulunan_takim}** bu sezon evinde maç başına ortalama **{gol_ort:.2f} gol** atıyor. Hücum hattı {'çok iyi' if gol_ort > 2 else 'ortalama'}."
                elif "form" in prompt_lower or "durum" in prompt_lower:
                    cevap = f"📈 **{bulunan_takim}** için verileri inceledim. İç saha performansı puanı: **{gol_ort*10:.0f}/30**. Detaylı analiz sekmesine bakmanı öneririm."
                elif "kazanır mı" in prompt_lower:
                    cevap = f"🤔 **{bulunan_takim}** maçı için rakibe de bakmam lazım. Analiz sekmesinden rakibi seçersen sana net yüzde veririm."
                else:
                    cevap = f"🤖 **{bulunan_takim}** hakkında istatistiklerim var. Gollerini mi yoksa form durumunu mu merak ediyorsun?"
            else:
                if "merhaba" in prompt_lower: cevap = "Selam! Bugün hangi maçı analiz edelim?"
                elif "kupon" in prompt_lower: cevap = "Otomatik kupon sekmesine geçersen sana günün bankolarını verebilirim."
        
        with st.chat_message("assistant"):
            st.write(cevap)
        st.session_state.messages.append({"role": "assistant", "content": cevap})
