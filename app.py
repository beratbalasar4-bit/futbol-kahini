import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.graph_objects as go
import time
import datetime
import random

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Futbol Kahini JARVIS", page_icon="🦁", layout="wide")

# --- CSS VE TASARIM ---
st.markdown("""
<style>
    .stApp { background-color: #0E1117; }
    h1 { color: #00CC96 !important; text-align: center; font-family: 'Arial Black', sans-serif; }
    
    /* Kart Tasarımları */
    .kupon-karti { background-color: #1F2937; padding: 15px; border-radius: 12px; margin-bottom: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); transition: transform 0.2s; }
    .kupon-karti:hover { transform: scale(1.02); }
    
    .banko-border { border-left: 8px solid #2ECC71; } /* Yeşil */
    .surpriz-border { border-left: 8px solid #E74C3C; } /* Kırmızı */
    
    .mac-baslik { color: white; font-weight: bold; font-size: 16px; margin: 0; }
    .tahmin-txt { color: #ccc; font-size: 14px; }
    .oran-badge { float: right; padding: 4px 10px; border-radius: 6px; font-weight: bold; color: white; font-size: 12px; }
    .bg-yesil { background-color: #2ECC71; }
    .bg-kirmizi { background-color: #E74C3C; }
    
    .stButton>button { 
        background: linear-gradient(to right, #00CC96, #00b887); 
        color: white; width: 100%; border-radius: 10px; height: 50px; border: none; font-weight: bold;
    }
    
    /* Sohbet Baloncukları */
    .stChatMessage { background-color: #262730; border-radius: 10px; border: 1px solid #444; }
</style>
""", unsafe_allow_html=True)

# --- VERİ VE AYARLAR ---
lig_kodlari = {
    "🇹🇷 Türkiye": "T1.csv", "🇬🇧 İngiltere": "E0.csv", "🇪🇸 İspanya": "SP1.csv",
    "🇩🇪 Almanya": "D1.csv", "🇮🇹 İtalya": "I1.csv", "🇫🇷 Fransa": "F1.csv"
}

takma_adlar = {
    "fener": "Fenerbahçe", "gs": "Galatasaray", "bjk": "Beşiktaş", "ts": "Trabzonspor",
    "city": "Manchester City", "united": "Manchester United", "real": "Real Madrid", "barca": "Barcelona"
}

takim_duzeltme = {
    "Fenerbahce": "Fenerbahçe", "Galatasaray": "Galatasaray", "Besiktas": "Beşiktaş", "Trabzonspor": "Trabzonspor",
    "Buyuksehyr": "Başakşehir FK", "Man City": "Manchester City", "Man United": "Manchester United",
    "Real Madrid": "Real Madrid", "Barcelona": "Barcelona", "Bayern Munich": "Bayern Münih",
    "Paris SG": "PSG", "Inter": "Inter Milan", "Milan": "AC Milan", "Juventus": "Juventus"
}

# --- GLOBAL VERİ YÜKLEYİCİ ---
@st.cache_data(ttl=3600)
def tum_verileri_yukle():
    tum_df = pd.DataFrame()
    ana_url = "https://www.football-data.co.uk/mmz4281/2425/"
    for lig_ad, dosya in lig_kodlari.items():
        try:
            url = ana_url + dosya
            df = pd.read_csv(url)
            df = df.dropna(subset=['FTR'])
            df['HomeTeam'] = df['HomeTeam'].replace(takim_duzeltme)
            df['AwayTeam'] = df['AwayTeam'].replace(takim_duzeltme)
            df['Lig'] = lig_ad 
            tum_df = pd.concat([tum_df, df])
        except: continue
    return tum_df

global_df = tum_verileri_yukle()
tum_takimlar = sorted(global_df['HomeTeam'].unique()) if not global_df.empty else []

# --- AKILLI SOHBET MOTORU (NLP SİMÜLASYONU) ---
def genel_kultur_cevapla(soru):
    soru = soru.lower()
    
    # 1. Genel Kültür Veritabanı (Basit Kurallar)
    bilgiler = {
        "başkent": {"türkiye": "Ankara", "ingiltere": "Londra", "fransa": "Paris", "almanya": "Berlin", "italya": "Roma", "ispanya": "Madrid"},
        "para birimi": {"türkiye": "Türk Lirası", "amerika": "Dolar", "avrupa": "Euro"},
        "başkanı": {"türkiye": "Recep Tayyip Erdoğan", "amerika": "Joe Biden"},
        "kaç gün": {"hafta": "7 gün", "yıl": "365 gün", "ay": "30 veya 31 gün"}
    }
    
    # 2. Cevap Arama
    for anahtar, detaylar in bilgiler.items():
        if anahtar in soru:
            for ulke, cevap in detaylar.items():
                if ulke in soru:
                    return f"🧠 **Bilgi:** {ulke.capitalize()} ülkesinin {anahtar}i: **{cevap}**"
    
    # 3. Geyik / Sohbet
    if "naber" in soru or "nasılsın" in soru:
        return "İyiyim! İşlemcim %100 performansta çalışıyor. Sen nasılsın?"
    elif "kimsin" in soru or "adın ne" in soru:
        return "Ben Berat'ın geliştirdiği Futbol Kahini AI. Futbol uzmanıyım ama genel kültürüm de fena değildir. 😉"
    elif "aşk" in soru or "sevgi" in soru:
        return "Ben bir yapay zekayım, aşktan anlamam ama 90. dakikada gelen golün hissini bilirim! ⚽"
    elif "hava" in soru:
        return "Hava durumunu bilemem ama bugün stadyum atmosferi çok sıcak olacak gibi duruyor!"
    
    return None # Cevap bulamazsa None döner (Futbol moduna geçer)

# --- ANALİZ MOTORU ---
def mac_analiz_et(ev, dep, df):
    ev_stats = df[df['HomeTeam'] == ev]
    dep_stats = df[df['AwayTeam'] == dep]
    if len(ev_stats) == 0 or len(dep_stats) == 0: return None

    # Gelişmiş Güç Hesabı
    ev_guc = (ev_stats['FTHG'].mean() * 35) - (ev_stats['FTAG'].mean() * 15) + 20
    dep_guc = (dep_stats['FTAG'].mean() * 35) - (dep_stats['FTHG'].mean() * 15) + 10
    gol_beklentisi = (ev_stats['FTHG'].mean() + dep_stats['FTAG'].mean()) / 2 + (dep_stats['FTHG'].mean() + ev_stats['FTAG'].mean()) / 2
    
    fark = ev_guc - dep_guc
    ibre = 50 + (fark / 1.5)
    return {"ibre": ibre, "gol": gol_beklentisi}

# --- ARAYÜZ ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3233/3233496.png", width=100)
    st.title("JARVIS AI")
    st.info(f"📅 Tarih: {datetime.datetime.now().strftime('%d.%m.%Y')}")
    st.caption("Otomatik Analiz Sistemi Devrede")

st.title("🌍 FUTBOL KAHİNİ (AI)")

# --- SEKME YAPISI ---
tab1, tab2, tab3 = st.tabs(["⚡ GÜNÜN OTOMATİK KUPONU", "📊 DETAYLI ANALİZ", "🤖 AKILLI SOHBET"])

# ================= SEKME 1: OTOMATİK KUPON (ZERO TOUCH) =================
with tab1:
    st.subheader(f"📅 {datetime.datetime.now().strftime('%d.%m.%Y')} - GÜNÜN RAPORU")
    
    # Kullanıcı bir şeye basmadan önce, sistemin çalıştığını göstermek için boş bir alan
    # Sadece ilk açılışta göstermek için session state kullanıyoruz
    if "kupon_hazir" not in st.session_state:
        st.session_state.kupon_hazir = False

    if not st.session_state.kupon_hazir:
        st.info("👋 Hoş geldin! Yapay zeka senin için bugünün en mantıklı maçlarını taramaya hazır.")
        if st.button("BUGÜNÜN KUPONLARINI GETİR 🎰", type="primary"):
            st.session_state.kupon_hazir = True
            st.rerun()
            
    if st.session_state.kupon_hazir:
        # --- OTOMATİK MAÇ SEÇİCİ (SIMULATION MODE) ---
        # Ücretsiz veride "bugün" tarihli maç olmayabilir.
        # Bu yüzden sistem liglerdeki "En Güçlü vs En Zayıf" veya "Derbi" potansiyelli maçları bulur.
        
        banko_liste = []
        surpriz_liste = []
        
        with st.spinner("Tüm Avrupa ligleri taranıyor... En iyi fırsatlar hesaplanıyor..."):
            time.sleep(1.5) # Analiz efekti
            
            tum_ligler = global_df['Lig'].unique()
            for lig in tum_ligler:
                df_lig = global_df[global_df['Lig'] == lig]
                if df_lig.empty: continue
                
                # Rastgele 4 takım seç (Bugünün fikstürü simülasyonu)
                takimlar = df_lig['HomeTeam'].unique()
                if len(takimlar) < 4: continue
                secilenler = random.sample(list(takimlar), 3) 
                
                for ev in secilenler:
                    # Analiz yap (Rakip ortalama bir takım gibi varsayılır hızlı tarama için)
                    stats = df_lig[df_lig['HomeTeam'] == ev]
                    puan = stats['FTHG'].mean() * 1.5 - stats['FTAG'].mean()
                    gol = stats['FTHG'].mean() + stats['FTAG'].mean()
                    
                    # BANKO KRİTERLERİ
                    if puan > 1.3:
                        banko_liste.append({"Lig": lig, "Maç": f"{ev} Kazanır", "Tahmin": "MS 1", "Oran": 1.45, "Güven": puan})
                    elif gol > 3.0:
                        banko_liste.append({"Lig": lig, "Maç": f"{ev} Maçı", "Tahmin": "2.5 ÜST", "Oran": 1.50, "Güven": gol})
                        
                    # SÜRPRİZ KRİTERLERİ
                    if -0.2 < puan < 0.2: # Maç ortadaysa beraberlik sürprizi
                        surpriz_liste.append({"Lig": lig, "Maç": f"{ev} Beraberlik", "Tahmin": "MS 0", "Oran": 3.40, "Güven": 5})
                    elif gol > 3.8:
                        surpriz_liste.append({"Lig": lig, "Maç": f"{ev} Gol Şov", "Tahmin": "3.5 ÜST", "Oran": 2.90, "Güven": 4})
        
        # LİSTELERİ SIRALA VE KES
        banko_final = sorted(banko_liste, key=lambda x: x['Güven'], reverse=True)[:3]
        surpriz_final = sorted(surpriz_liste, key=lambda x: x['Oran'], reverse=True)[:3]
        
        c1, c2 = st.columns(2)
        
        # --- BANKO KUPON KARTI ---
        with c1:
            st.success("✅ GÜNÜN BANKO KUPONU")
            toplam_oran = 1.0
            for mac in banko_final:
                toplam_oran *= mac['Oran']
                st.markdown(f"""
                <div class="kupon-karti banko-border">
                    <span class="oran-badge bg-yesil">{mac['Oran']}</span>
                    <div class="mac-baslik">{mac['Maç']}</div>
                    <div style="font-size:12px; color:#aaa;">{mac['Lig']}</div>
                    <div class="tahmin-txt">Tahmin: <b>{mac['Tahmin']}</b></div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown(f"**Toplam Oran: {toplam_oran:.2f}**")
            
        # --- SÜRPRİZ KUPON KARTI ---
        with c2:
            st.error("🔥 GÜNÜN SÜRPRİZ KUPONU")
            toplam_oran_s = 1.0
            for mac in surpriz_final:
                toplam_oran_s *= mac['Oran']
                st.markdown(f"""
                <div class="kupon-karti surpriz-border">
                    <span class="oran-badge bg-kirmizi">{mac['Oran']}</span>
                    <div class="mac-baslik">{mac['Maç']}</div>
                    <div style="font-size:12px; color:#aaa;">{mac['Lig']}</div>
                    <div class="tahmin-txt">Tahmin: <b>{mac['Tahmin']}</b></div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown(f"**Toplam Oran: {toplam_oran_s:.2f}**")
            
        st.button("🔄 Kuponları Yenile") # Tekrar basarsa yeniden üretir

# ================= SEKME 2: MANUEL ANALİZ =================
with tab2:
    st.info("Kendi maçını kendin seçmek istersen buradan detaylı analiz yapabilirsin.")
    lig = st.selectbox("Lig Seç:", list(lig_kodlari.keys()))
    df_lig = global_df[global_df['Lig'] == lig]
    c_1, c_2 = st.columns(2)
    takimlar_lig = sorted(df_lig['HomeTeam'].unique())
    with c_1: ev = st.selectbox("Ev Sahibi", takimlar_lig)
    with c_2: dep = st.selectbox("Deplasman", takimlar_lig, index=1)
    
    if st.button("ANALİZ ET 🔎"):
        sonuc = mac_analiz_et(ev, dep, df_lig)
        if sonuc:
            fig = go.Figure(go.Indicator(
                mode = "gauge+number", value = sonuc['ibre'], title = {'text': "Kazanma Şansı %"},
                gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': "white"}, 'steps': [{'range': [0, 45], 'color': "#FF4B4B"}, {'range': [55, 100], 'color': "#00CC96"}]}
            ))
            fig.update_layout(height=250, margin=dict(t=30,b=20,l=20,r=20), paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
            st.write(f"Gol Beklentisi: **{sonuc['gol']:.2f}**")

# ================= SEKME 3: SOHBET ROBOTU (GENEL KÜLTÜR + FUTBOL) =================
with tab3:
    st.subheader("💬 AI ASİSTAN İLE KONUŞ")
    st.caption("Futbol, başkentler, genel kültür... Her şeyi sorabilirsin.")

    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Selam! Ben Jarvis. Bugün sana nasıl yardım edebilirim?"}]

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.write(msg["content"])

    if prompt := st.chat_input("Sorunu yaz..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.write(prompt)

        # --- CEVAP MEKANİZMASI ---
        cevap = ""
        prompt_lower = prompt.lower()
        
        # 1. ÖNCE GENEL KÜLTÜR KONTROLÜ
        genel_cevap = genel_kultur_cevapla(prompt)
        if genel_cevap:
            cevap = genel_cevap
        
        # 2. FUTBOL ANALİZİ KONTROLÜ
        else:
            # Takım isimlerini bul
            bulunanlar = []
            for kisa, uzun in takma_adlar.items():
                if kisa in prompt_lower.split(): 
                    if uzun not in bulunanlar: bulunanlar.append(uzun)
            for takim in tum_takimlar:
                if takim.lower() in prompt_lower:
                    if takim not in bulunanlar: bulunanlar.append(takim)
            
            if len(bulunanlar) >= 2:
                ev, dep = bulunanlar[0], bulunanlar[1]
                sonuc = mac_analiz_et(ev, dep, global_df)
                if sonuc:
                    kazanan = ev if sonuc['ibre'] > 55 else (dep if sonuc['ibre'] < 45 else "Beraberlik")
                    cevap = f"⚽ **{ev} vs {dep}** Analizi:\n\nVerilere göre **{kazanan}** tarafı avantajlı. Gol beklentisi {sonuc['gol']:.2f}. Bence güzel maç olur!"
                else: cevap = "Bu takımların verisi eksik."
            elif len(bulunanlar) == 1:
                cevap = f"🤔 Sadece **{bulunanlar[0]}** takımını yazdın. Rakibi kim? İkisini yazarsan analiz ederim."
            else:
                cevap = "Bunu tam anlamadım. Ya bir maç sor (ör: Fener Gala maçı) ya da genel bir soru sor (ör: Türkiye başkenti)."

        with st.chat_message("assistant"): st.write(cevap)
        st.session_state.messages.append({"role": "assistant", "content": cevap})
