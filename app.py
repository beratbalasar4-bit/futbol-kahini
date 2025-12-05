import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.graph_objects as go
import time
import datetime
import random

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Futbol Kahini AI", page_icon="🧠", layout="wide")

# --- CSS VE TASARIM ---
st.markdown("""
<style>
    .stApp { background-color: #0E1117; }
    h1 { color: #00CC96 !important; text-align: center; font-family: 'Arial Black', sans-serif; }
    
    /* Kupon Tasarımı */
    .kupon-karti { background-color: #1F2937; padding: 15px; border-radius: 12px; border: 1px solid #374151; margin-bottom: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
    .banko-border { border-left: 8px solid #00CC96; }
    .surpriz-border { border-left: 8px solid #F39C12; }
    
    .mac-baslik { color: white; font-weight: bold; font-size: 16px; margin: 0; }
    .tahmin-txt { color: #ccc; font-size: 14px; }
    .oran-badge { float: right; padding: 4px 10px; border-radius: 6px; font-weight: bold; color: white; font-size: 12px; }
    .oran-yesil { background-color: #00CC96; }
    .oran-turuncu { background-color: #F39C12; }
    
    /* Sohbet */
    .stChatMessage { background-color: #262730; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# --- VERİ SETLERİ ---
lig_kodlari = {
    "🇹🇷 Türkiye": "T1.csv", "🇬🇧 İngiltere": "E0.csv", "🇪🇸 İspanya": "SP1.csv",
    "🇩🇪 Almanya": "D1.csv", "🇮🇹 İtalya": "I1.csv", "🇫🇷 Fransa": "F1.csv", "🇳🇱 Hollanda": "N1.csv"
}

takma_adlar = {
    "fener": "Fenerbahçe", "fb": "Fenerbahçe", "gala": "Galatasaray", "gs": "Galatasaray",
    "bjk": "Beşiktaş", "ts": "Trabzonspor", "city": "Manchester City", "united": "Manchester United",
    "real": "Real Madrid", "barca": "Barcelona", "bayern": "Bayern Munich", "mainz": "Mainz",
    "gladbach": "M'gladbach", "dortmund": "Dortmund"
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
    
    # Korner
    korner = 9.0
    if 'HC' in df.columns:
        korner = (ev_stats['HC'].mean() + dep_stats['AC'].mean()) 

    fark = ev_guc - dep_guc
    ibre = 50 + (fark / 1.5)
    return {"ibre": ibre, "gol": gol_beklentisi, "korner": korner}

# --- ANA SAYFA ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3233/3233496.png", width=100)
    st.markdown("### 🦁 SÜPER ASİSTAN")
    st.success(f"📅 Tarih: {datetime.datetime.now().strftime('%d.%m.%Y')}")
    st.info("Canlı Skor'dan bugünün maçlarına bak, kupon sekmesinde o takımları seç!")

st.title("🌍 FUTBOL KAHİNİ AI")

# --- CANLI SKOR (MAÇ PROGRAMI İÇİN) ---
with st.expander("📅 BUGÜNÜN MAÇ PROGRAMI (Canlı Skor)", expanded=False):
    components.html("""<iframe src="https://www.livescore.bz" width="100%" height="600" frameborder="0" style="background-color: white; border-radius: 8px;"></iframe>""", height=600, scrolling=True)

# --- SEKME YAPISI ---
tab1, tab2, tab3 = st.tabs(["🎟️ KUPON OLUŞTURUCU", "📊 TEK MAÇ ANALİZİ", "🤖 SOHBET"])

# ================= SEKME 1: AKILLI KUPON OLUŞTURUCU =================
with tab1:
    st.subheader("🎯 HANGİ MAÇLARA KUPON YAPALIM?")
    st.markdown("Yukarıdaki fikstürden bugün oynayan maçları seç, **Banko** ve **Sürpriz** kuponunu ben hazırlayayım.")
    
    # 1. Kullanıcı Bugün Oynayan Takımları Seçer (Manuel ama Kesin Çözüm)
    secilen_takimlar = st.multiselect("Bugün Maçı Olan Ev Sahibi Takımları Seç:", tum_takimlar, placeholder="Örn: Mainz, Fenerbahçe, Arsenal...")
    
    col_k1, col_k2 = st.columns(2)
    
    if st.button("KUPONLARI HAZIRLA 🚀", type="primary"):
        if not secilen_takimlar:
            st.error("Lütfen en az 1 takım seç!")
        else:
            with st.spinner("Yapay zeka seçtiğin maçları analiz ediyor..."):
                time.sleep(1)
                
                banko_kupon = []
                surpriz_kupon = []
                
                for ev_sahibi in secilen_takimlar:
                    # Bu ev sahibinin oynadığı ligi ve rakibini bulmamız lazım
                    # (Otomatik bulmaya çalışıyoruz, son maç verisinden ligi tahmin ediyoruz)
                    takim_data = global_df[global_df['HomeTeam'] == ev_sahibi]
                    if not takim_data.empty:
                        lig = takim_data.iloc[0]['Lig']
                        # Rakibi bulmak zor olduğu için simülasyon yerine
                        # Kullanıcıya sadece Ev Sahibi analizi veriyoruz VEYA
                        # Kullanıcıya rakibi de seçtirebiliriz ama bu çok uzun sürer.
                        # Basitlik için: Ev sahibinin GENEL GÜCÜNE göre tahmin yapıyoruz.
                        
                        ev_guc = takim_data['FTHG'].mean() * 1.5 - takim_data['FTAG'].mean()
                        gol_ort = takim_data['FTHG'].mean() + takim_data['FTAG'].mean()
                        
                        # --- BANKO MANTIK ---
                        if ev_guc > 1.2:
                            banko_kupon.append({"Maç": f"{ev_sahibi} Kazanır", "Tahmin": "MS 1", "Oran": 1.45, "Güven": ev_guc})
                        elif gol_ort > 3.0:
                            banko_kupon.append({"Maç": f"{ev_sahibi} Maçı", "Tahmin": "2.5 ÜST", "Oran": 1.55, "Güven": gol_ort})
                        else:
                            # Banko çıkmazsa Sürprize at
                            pass
                            
                        # --- SÜRPRİZ MANTIK ---
                        if 0 < ev_guc < 0.5: # Güç farkı azsa beraberlik
                            surpriz_kupon.append({"Maç": f"{ev_sahibi} Beraberlik", "Tahmin": "MS 0", "Oran": 3.20, "Güven": 5})
                        elif gol_ort > 3.5:
                            surpriz_kupon.append({"Maç": f"{ev_sahibi} Maçı", "Tahmin": "3.5 ÜST", "Oran": 2.80, "Güven": 4})

                # --- SONUÇLARI GÖSTER ---
                
                # SOL TARAFA BANKO
                with col_k1:
                    st.success("🔒 GÜNÜN BANKO KUPONU")
                    st.caption("Düşük Risk, Mantıklı Tercihler")
                    if banko_kupon:
                        toplam_oran = 1.0
                        for mac in banko_kupon[:3]: # En iyi 3
                            toplam_oran *= mac['Oran']
                            st.markdown(f"""
                            <div class="kupon-karti banko-border">
                                <span class="oran-badge oran-yesil">{mac['Oran']}</span>
                                <div class="mac-baslik">{mac['Maç']}</div>
                                <div class="tahmin-txt">Tahmin: <b>{mac['Tahmin']}</b></div>
                            </div>
                            """, unsafe_allow_html=True)
                        st.markdown(f"**Toplam Oran: {toplam_oran:.2f}**")
                    else:
                        st.warning("Seçtiğin takımlardan banko fırsat çıkmadı.")

                # SAĞ TARAFA SÜRPRİZ
                with col_k2:
                    st.warning("🔥 GÜNÜN SÜRPRİZ KUPONU")
                    st.caption("Yüksek Oran, Yüksek Kazanç")
                    if surpriz_kupon:
                        toplam_oran_s = 1.0
                        for mac in surpriz_kupon[:3]:
                            toplam_oran_s *= mac['Oran']
                            st.markdown(f"""
                            <div class="kupon-karti surpriz-border">
                                <span class="oran-badge oran-turuncu">{mac['Oran']}</span>
                                <div class="mac-baslik">{mac['Maç']}</div>
                                <div class="tahmin-txt">Tahmin: <b>{mac['Tahmin']}</b></div>
                            </div>
                            """, unsafe_allow_html=True)
                        st.markdown(f"**Toplam Oran: {toplam_oran_s:.2f}**")
                    else:
                        st.info("Bu maçlarda sürpriz potansiyeli düşük.")

# ================= SEKME 2: TEK MAÇ ANALİZİ =================
with tab2:
    st.subheader("📊 DETAYLI KARŞILAŞTIRMA")
    lig = st.selectbox("Lig Seç:", list(lig_kodlari.keys()))
    df_lig = global_df[global_df['Lig'] == lig]
    
    c1, c2 = st.columns(2)
    takimlar_lig = sorted(df_lig['HomeTeam'].unique())
    with c1: ev = st.selectbox("Ev Sahibi", takimlar_lig)
    with c2: dep = st.selectbox("Deplasman", takimlar_lig, index=1)
    
    if st.button("ANALİZ ET 🚀"):
        sonuc = mac_analiz_et(ev, dep, df_lig)
        if sonuc:
            col_g1, col_g2 = st.columns([2,1])
            with col_g1:
                fig = go.Figure(go.Indicator(
                    mode = "gauge+number", value = sonuc['ibre'],
                    title = {'text': "Kazanma Şansı %"},
                    gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': "white"}, 'steps': [{'range': [0, 45], 'color': "#FF4B4B"}, {'range': [55, 100], 'color': "#00CC96"}]}
                ))
                fig.update_layout(height=250, margin=dict(t=30,b=20,l=20,r=20), paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True)
            
            with col_g2:
                st.info(f"⚽ Gol Beklentisi: **{sonuc['gol']:.2f}**")
                st.warning(f"⛳ Korner Tahmini: **{sonuc['korner']:.1f}**")
                
                if sonuc['gol'] > 2.8: st.success("✅ **2.5 ÜST** Biter")
                else: st.error("🧊 **2.5 ALT** Biter")
        else: st.error("Veri Yok")

# ================= SEKME 3: SOHBET ROBOTU =================
with tab3:
    st.subheader("💬 SOHBET ET")
    st.caption("Hem maç sorabilirsin, hem sohbet edebilirsin.")

    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Selam! Ben senin futbol asistanınım. Bugün hangi maça bakalım?"}]

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.write(msg["content"])

    if prompt := st.chat_input("Mesajını yaz..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.write(prompt)

        # --- GELİŞMİŞ SOHBET MOTORU ---
        prompt_lower = prompt.lower()
        cevap = ""

        # 1. Sohbet / Geyik Modu
        sohbet_kelimeleri = ["naber", "nasılsın", "nasilsin", "ne haber"]
        kimsin_kelimeleri = ["kimsin", "adın ne", "sen kimsin"]
        
        if any(x in prompt_lower for x in sohbet_kelimeleri):
            cevap = random.choice(["İyiyim patron, maçları analiz ediyorum. Sen nasılsın?", "Bomba gibiyim! Bugün güzel kuponlar çıkaracağız.", "Kodlarım tıkır tıkır çalışıyor, gole açım!"])
        elif any(x in prompt_lower for x in kimsin_kelimeleri):
            cevap = "Ben Futbol Kahini. Yapay zeka ile istatistikleri çiğneyip sana banko kuponlar sunan dijital asistanım. 🦁"
        
        # 2. Maç Analiz Modu
        else:
            # Takımları Bul
            bulunanlar = []
            for kisa, uzun in takma_adlar.items(): # Önce takma adlar
                if kisa in prompt_lower.split(): 
                    if uzun not in bulunanlar: bulunanlar.append(uzun)
            
            for takim in tum_takimlar: # Sonra gerçek adlar
                if takim.lower() in prompt_lower:
                    if takim not in bulunanlar: bulunanlar.append(takim)

            if len(bulunanlar) >= 2:
                ev, dep = bulunanlar[0], bulunanlar[1]
                sonuc = mac_analiz_et(ev, dep, global_df)
                if sonuc:
                    favori = ev if sonuc['ibre'] > 55 else (dep if sonuc['ibre'] < 45 else "Beraberlik")
                    cevap = f"📊 **{ev} vs {dep}** kapışması!\n\nVerilere baktım, ibre **{favori}** tarafını gösteriyor. Gol beklentisi **{sonuc['gol']:.2f}**. Bence maçta bol pozisyon olur."
                else: cevap = "Bu takımların verilerini bulamadım."
            elif len(bulunanlar) == 1:
                cevap = f"🤔 **{bulunanlar[0]}** hakkında konuşuyorsun. Tek takım analiz edemem, rakibini de söyle kapıştırayım!"
            else:
                if not cevap: # Sohbet de değilse
                    cevap = "Bunu tam anlamadım. Takım adı yazarsan analiz ederim, ya da 'naber' yaz sohbet edelim."

        with st.chat_message("assistant"): st.write(cevap)
        st.session_state.messages.append({"role": "assistant", "content": cevap})
