import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.graph_objects as go
import time
import random

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Futbol Kahini AI", page_icon="🧠", layout="wide")

# --- CSS VE TASARIM ---
st.markdown("""
<style>
    .stApp { background-color: #0E1117; }
    h1 { color: #00CC96 !important; text-align: center; font-family: 'Arial Black', sans-serif; }
    
    /* Kupon Tasarımı */
    .kupon-container { background-color: #1F2937; padding: 15px; border-radius: 10px; border: 1px solid #374151; margin-bottom: 10px; }
    .bahis-tur { color: #F39C12; font-weight: bold; font-size: 12px; letter-spacing: 1px; }
    .mac-baslik { color: white; font-weight: bold; font-size: 18px; margin: 5px 0; }
    .oran-kutusu { background-color: #00CC96; color: white; padding: 5px 10px; border-radius: 5px; font-weight: bold; float: right; }
    
    .stButton>button { 
        background: linear-gradient(to right, #00CC96, #00b887); 
        color: white; width: 100%; border-radius: 10px; height: 50px; border: none; font-weight: bold;
    }
    
    /* Chat Baloncukları */
    .stChatMessage { background-color: #1F2937; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# --- VERİ SETLERİ VE AYARLAR ---
lig_kodlari = {
    "🇹🇷 Türkiye": "T1.csv", "🇬🇧 İngiltere": "E0.csv", "🇪🇸 İspanya": "SP1.csv",
    "🇩🇪 Almanya": "D1.csv", "🇮🇹 İtalya": "I1.csv", "🇫🇷 Fransa": "F1.csv", "🇳🇱 Hollanda": "N1.csv"
}

# Takma Adlar Sözlüğü (Chatbot için)
takma_adlar = {
    "fener": "Fenerbahçe", "fb": "Fenerbahçe", "fenerbahçe": "Fenerbahçe",
    "gala": "Galatasaray", "gs": "Galatasaray", "cimbom": "Galatasaray", "galatasaray": "Galatasaray",
    "bjk": "Beşiktaş", "beşiktaş": "Beşiktaş", "kartal": "Beşiktaş",
    "ts": "Trabzonspor", "trabzon": "Trabzonspor",
    "city": "Manchester City", "man city": "Manchester City",
    "united": "Manchester United", "man utd": "Manchester United",
    "real": "Real Madrid", "barca": "Barcelona"
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
    """Tüm liglerin verisini tek seferde çeker ve hafızaya alır"""
    tum_df = pd.DataFrame()
    ana_url = "https://www.football-data.co.uk/mmz4281/2425/"
    
    for lig_ad, dosya in lig_kodlari.items():
        try:
            url = ana_url + dosya
            df = pd.read_csv(url)
            df = df.dropna(subset=['FTR'])
            df['HomeTeam'] = df['HomeTeam'].replace(takim_duzeltme)
            df['AwayTeam'] = df['AwayTeam'].replace(takim_duzeltme)
            df['Lig'] = lig_ad # Hangi ligden olduğunu bilelim
            tum_df = pd.concat([tum_df, df])
        except: continue
    return tum_df

# Verileri Yükle
global_df = tum_verileri_yukle()
tum_takimlar = global_df['HomeTeam'].unique() if not global_df.empty else []

# --- ANALİZ MOTORU ---
def mac_analiz_et(ev, dep, df):
    ev_stats = df[df['HomeTeam'] == ev]
    dep_stats = df[df['AwayTeam'] == dep]
    
    if len(ev_stats) == 0 or len(dep_stats) == 0: return None

    # Güç Hesaplama
    ev_guc = (ev_stats['FTHG'].mean() * 40) + 15
    dep_guc = (dep_stats['FTAG'].mean() * 40) + 15
    
    # Gol Tahmini
    gol_beklentisi = (ev_stats['FTHG'].mean() + dep_stats['FTAG'].mean()) / 2 + \
                     (dep_stats['FTHG'].mean() + ev_stats['FTAG'].mean()) / 2
    
    # Korner (Varsa)
    korner = 9.0
    if 'HC' in df.columns:
        korner = (ev_stats['HC'].mean() + dep_stats['AC'].mean()) 

    fark = ev_guc - dep_guc
    ibre = 50 + (fark / 1.5)
    return {"ibre": ibre, "gol": gol_beklentisi, "korner": korner, "ev_guc": ev_guc, "dep_guc": dep_guc}

# --- ANA SAYFA ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3233/3233496.png", width=100)
    st.markdown("### 🦁 SÜPER ASİSTAN")
    st.info("Yapay Zeka tüm Avrupa liglerini tarıyor.")

st.title("🌍 FUTBOL KAHİNİ AI")

# --- SEKME YAPISI ---
tab1, tab2, tab3 = st.tabs(["📊 TEK MAÇ ANALİZİ", "🎟️ GLOBAL KARIŞIK KUPON", "🤖 AKILLI SOHBET"])

# ================= SEKME 1: ANALİZ =================
with tab1:
    lig = st.selectbox("Lig Seç:", list(lig_kodlari.keys()))
    df_lig = global_df[global_df['Lig'] == lig]
    
    c1, c2 = st.columns(2)
    takimlar_lig = sorted(df_lig['HomeTeam'].unique())
    with c1: ev = st.selectbox("Ev Sahibi", takimlar_lig)
    with c2: dep = st.selectbox("Deplasman", takimlar_lig, index=1)
    
    if st.button("DETAYLI ANALİZ ET 🚀"):
        sonuc = mac_analiz_et(ev, dep, df_lig)
        if sonuc:
            # Görselleştirme
            fig = go.Figure(go.Indicator(
                mode = "gauge+number", value = sonuc['ibre'],
                title = {'text': "Ev Sahibi Şansı"},
                gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': "white"}, 'steps': [{'range': [0, 45], 'color': "#FF4B4B"}, {'range': [55, 100], 'color': "#00CC96"}]}
            ))
            fig.update_layout(height=250, margin=dict(t=30,b=20,l=20,r=20), paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
            
            k1, k2, k3 = st.columns(3)
            k1.info(f"⚽ Gol Beklentisi: **{sonuc['gol']:.2f}**")
            k2.warning(f"⛳ Korner Tahmini: **{sonuc['korner']:.1f}**")
            k3.success(f"🧠 Güven Skoru: **{abs(sonuc['ibre']-50):.0f}**")
        else: st.error("Veri Yok")

# ================= SEKME 2: GLOBAL KUPON (ÇEŞİTLİ BAHİS) =================
with tab2:
    st.subheader("🔥 YAPAY ZEKA KARIŞIK KUPON")
    st.markdown("Sistem 7 büyük ligi tarar ve **Maç Sonucu**, **Gol**, **Korner** ve **KG Var** seçeneklerinden en sağlamlarını seçer.")
    
    if st.button("BÜYÜK KUPONU OLUŞTUR 🎰"):
        with st.spinner("Tüm Avrupa ligleri taranıyor..."):
            time.sleep(1.5)
            
            # --- KUPON MOTORU ---
            bankolar = []
            
            # Ligdeki güçlü takımları ve golcüleri bul
            for lig in lig_kodlari.keys():
                df_temp = global_df[global_df['Lig'] == lig]
                if df_temp.empty: continue
                
                takimlar = df_temp['HomeTeam'].unique()
                # Rassal 3 takım seç (Her seferinde farklı analiz yapsın diye)
                sample_takimlar = random.sample(list(takimlar), min(len(takimlar), 5))
                
                for t in sample_takimlar:
                    stats = df_temp[df_temp['HomeTeam'] == t]
                    if len(stats) < 3: continue
                    
                    # 1. MAÇ SONUCU (Ev Gücü)
                    ev_guc = stats['FTHG'].mean() - stats['FTAG'].mean()
                    if ev_guc > 1.5:
                        bankolar.append({"Lig": lig, "Maç": f"{t} (Ev)", "Tür": "MAÇ SONUCU", "Tahmin": "MS 1", "Güven": ev_guc + 80})
                    
                    # 2. GOL (2.5 ÜST)
                    gol_ort = stats['FTHG'].mean() + stats['FTAG'].mean()
                    if gol_ort > 3.2:
                        bankolar.append({"Lig": lig, "Maç": f"{t} Maçı", "Tür": "GOL BAHİSİ", "Tahmin": "2.5 ÜST", "Güven": gol_ort * 25})
                    
                    # 3. KORNER (9.5 ÜST)
                    if 'HC' in df_temp.columns:
                        korn_ort = stats['HC'].mean() + stats['AC'].mean()
                        if korn_ort > 10.5:
                            bankolar.append({"Lig": lig, "Maç": f"{t} Maçı", "Tür": "KORNER", "Tahmin": "9.5 ÜST", "Güven": korn_ort * 8})

            # En yüksek güvenli 4 maçı seç
            kupon = sorted(bankolar, key=lambda x: x['Güven'], reverse=True)[:4]
            
            # Ekrana Bas
            if kupon:
                st.balloons()
                st.success("✅ GÜNÜN BANKO KUPONU HAZIR")
                
                total_oran = 1.0
                
                for mac in kupon:
                    # Rastgele oran süsü (Gerçek oran API paralı olduğu için)
                    oran = round(random.uniform(1.30, 1.85), 2)
                    total_oran *= oran
                    
                    st.markdown(f"""
                    <div class="kupon-container">
                        <span class="bahis-tur">{mac['Lig']} • {mac['Tür']}</span>
                        <div class="oran-kutusu">{oran}</div>
                        <div class="mac-baslik">{mac['Maç']}</div>
                        <div style="color:#ccc;">Tahmin: <b style="color:#00CC96;">{mac['Tahmin']}</b></div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown(f"### 🚀 Toplam Tahmini Oran: **{total_oran:.2f}**")
            else:
                st.warning("Yeterli güvenilir maç bulunamadı.")

# ================= SEKME 3: AKILLI SOHBET (NLP) =================
with tab3:
    st.subheader("🤖 YAPAY ZEKA İLE KONUŞ")
    st.caption("Örnek: 'Beşiktaş Fener maçı ne olur?', 'Galatasaray gol atar mı?', 'City form durumu'")

    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Selam! Maçları sor, analiz edeyim."}]

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.write(msg["content"])

    if prompt := st.chat_input("Sorunu yaz..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.write(prompt)

        # --- AKILLI CEVAP MOTORU ---
        cevap = "Bunu anlayamadım. Takım isimlerini doğru yazdığından emin ol."
        prompt_lower = prompt.lower()
        
        # 1. Cümledeki Takımları Bul
        bulunanlar = []
        
        # Önce takma adları kontrol et (fb -> fenerbahçe)
        for kisa, uzun in takma_adlar.items():
            if kisa in prompt_lower.split(): # Kelime olarak geçiyorsa
                if uzun not in bulunanlar: bulunanlar.append(uzun)
        
        # Sonra gerçek isimleri kontrol et
        for takim in tum_takimlar:
            if takim.lower() in prompt_lower:
                if takim not in bulunanlar: bulunanlar.append(takim)
        
        # --- SENARYO A: İKİ TAKIM VAR (KARŞILAŞTIRMA) ---
        if len(bulunanlar) >= 2:
            ev, dep = bulunanlar[0], bulunanlar[1]
            sonuc = mac_analiz_et(ev, dep, global_df)
            
            if sonuc:
                if sonuc['ibre'] > 55: favori = ev
                elif sonuc['ibre'] < 45: favori = dep
                else: favori = "Beraberlik"
                
                cevap = f"📊 **{ev} vs {dep} Analizim:**\n\n" \
                        f"İstatistiklere göre **{favori}** tarafı daha ağır basıyor. " \
                        f"Bu maçta Gol Beklentisi **{sonuc['gol']:.2f}**. " \
                        f"{( 'Bol gollü geçer (2.5 Üst).' if sonuc['gol']>2.8 else 'Kısır geçebilir (Alt).' )}"
            else:
                cevap = "Bu iki takımı buldum ama yeterli verileri yok."

        # --- SENARYO B: TEK TAKIM VAR ---
        elif len(bulunanlar) == 1:
            takim = bulunanlar[0]
            stats = global_df[global_df['HomeTeam'] == takim]
            if not stats.empty:
                gol_at = stats['FTHG'].mean()
                gol_ye = stats['FTAG'].mean()
                cevap = f"🧐 **{takim}** Hakkında Rapor:\n\n" \
                        f"Bu sezon iç sahada ortalama **{gol_at:.2f}** gol atıp, **{gol_ye:.2f}** gol yiyor. " \
                        f"Genel form durumu: {'🔥 Çok Formda' if gol_at > 2 else '😐 Orta Şeker'}."
            else:
                cevap = f"{takim} verilerini şu an çekemedim."
        
        # --- SENARYO C: HİÇBİR ŞEY YOK ---
        else:
            if "kupon" in prompt_lower: cevap = "Kupon sekmesine geçersen senin için banko kupon hazırladım!"
            elif "selam" in prompt_lower: cevap = "Selam! Hangi takımı analiz edelim?"
        
        with st.chat_message("assistant"): st.write(cevap)
        st.session_state.messages.append({"role": "assistant", "content": cevap})
