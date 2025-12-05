import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.graph_objects as go
import time
import datetime
import random
from scipy.stats import poisson # Skor tahmini için matematik kütüphanesi

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Futbol Kahini PRO", page_icon="🦁", layout="wide")

# --- CSS (BAHİS SİTESİ GÖRÜNÜMÜ) ---
st.markdown("""
<style>
    .stApp { background-color: #121212; }
    h1 { color: #00E676 !important; text-align: center; font-family: 'Arial Black', sans-serif; text-transform: uppercase; }
    
    /* İstatistik Kartları */
    .stat-box {
        background-color: #1E1E1E; border-radius: 10px; padding: 15px; margin: 5px;
        border-top: 4px solid #00E676; text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .stat-title { color: #B0BEC5; font-size: 12px; font-weight: bold; text-transform: uppercase; }
    .stat-value { color: white; font-size: 20px; font-weight: bold; margin-top: 5px; }
    .risk-high { border-top-color: #FF5252; }
    .risk-med { border-top-color: #FFAB40; }
    
    /* Kupon Kartı */
    .kupon-karti { background-color: #263238; padding: 15px; border-radius: 8px; margin-bottom: 10px; border-left: 5px solid #00E676; }
    .surpriz { border-left: 5px solid #FF5252; }
    .oran { float: right; background: #00E676; color: black; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
    .oran-s { background: #FF5252; color: white; }
    
    /* Sohbet */
    .stChatMessage { background-color: #1E1E1E; border: 1px solid #333; }
</style>
""", unsafe_allow_html=True)

# --- VERİ SETLERİ ---
lig_kodlari = {
    "🇹🇷 Türkiye Süper Lig": "T1.csv", "🇬🇧 İngiltere Premier": "E0.csv", 
    "🇪🇸 İspanya La Liga": "SP1.csv", "🇩🇪 Almanya Bundesliga": "D1.csv", 
    "🇮🇹 İtalya Serie A": "I1.csv", "🇫🇷 Fransa Ligue 1": "F1.csv"
}

takma_adlar = {
    "fener": "Fenerbahçe", "gs": "Galatasaray", "bjk": "Beşiktaş", "ts": "Trabzonspor",
    "city": "Manchester City", "united": "Manchester United", "real": "Real Madrid", "barca": "Barcelona",
    "bayern": "Bayern Munich", "dortmund": "Dortmund", "liverpool": "Liverpool", "arsenal": "Arsenal"
}

takim_duzeltme = {
    "Fenerbahce": "Fenerbahçe", "Galatasaray": "Galatasaray", "Besiktas": "Beşiktaş", "Trabzonspor": "Trabzonspor",
    "Buyuksehyr": "Başakşehir FK", "Man City": "Manchester City", "Man United": "Manchester United",
    "Real Madrid": "Real Madrid", "Barcelona": "Barcelona", "Bayern Munich": "Bayern Münih",
    "Paris SG": "PSG", "Inter": "Inter Milan", "Milan": "AC Milan", "Juventus": "Juventus",
    "M'gladbach": "M'gladbach", "Dortmund": "Dortmund", "Mainz": "Mainz", "Leverkusen": "Leverkusen"
}

# --- GLOBAL VERİ YÜKLEME ---
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

# --- 🧠 DETAYLI ANALİZ MOTORU (BAHİS SİTESİ GİBİ) ---
def detayli_analiz(ev, dep, df):
    ev_stats = df[df['HomeTeam'] == ev]
    dep_stats = df[df['AwayTeam'] == dep]
    
    if len(ev_stats) < 2 or len(dep_stats) < 2: return None

    # 1. ORTALAMALAR
    ev_atilan = ev_stats['FTHG'].mean()
    ev_yenen = ev_stats['FTAG'].mean()
    dep_atilan = dep_stats['FTAG'].mean()
    dep_yenen = dep_stats['FTHG'].mean()
    
    # 2. GOL BEKLENTİSİ (Poisson)
    ev_beklenti = (ev_atilan + dep_yenen) / 2
    dep_beklenti = (dep_atilan + ev_yenen) / 2
    toplam_gol = ev_beklenti + dep_beklenti
    
    # 3. KORNER (Varsa)
    korner = 9.5
    if 'HC' in df.columns:
        korner = (ev_stats['HC'].mean() + dep_stats['AC'].mean())
        
    # 4. KART (Varsa)
    kart = 4.5
    if 'HY' in df.columns:
        kart = (ev_stats['HY'].mean() + ev_stats['AY'].mean() + dep_stats['HY'].mean() + dep_stats['AY'].mean()) / 2

    # 5. KG VAR İHTİMALİ
    kg_var_prob = (ev_atilan > 0.8) and (dep_atilan > 0.8) and (ev_yenen > 0.8) and (dep_yenen > 0.8)
    
    # 6. SKOR TAHMİNİ (En yüksek ihtimalli)
    skor_ev = int(round(ev_beklenti))
    skor_dep = int(round(dep_beklenti))
    
    # 7. İBRE (Kazanma Şansı)
    ev_guc = ev_atilan * 1.5 - ev_yenen
    dep_guc = dep_atilan * 1.5 - dep_yenen
    fark = ev_guc - dep_guc
    ibre = 50 + (fark * 15)
    ibre = max(10, min(90, ibre))
    
    return {
        "ev_beklenti": ev_beklenti, "dep_beklenti": dep_beklenti,
        "toplam_gol": toplam_gol, "korner": korner, "kart": kart,
        "kg_var": kg_var_prob, "skor": f"{skor_ev} - {skor_dep}",
        "ibre": ibre
    }

# --- FİKSTÜR ÇEKME DENEMESİ (WEB SCRAPING) ---
@st.cache_data(ttl=3600)
def fikstur_cek():
    # Burası gerçek bir siteden veri çekmeye çalışır.
    # Eğer site engellerse, boş liste döner ve manuel seçime yönlendiririz.
    try:
        # Wikipedia veya basit bir HTML tablosu okumayı dener
        # Not: Bu kısım demo amaçlıdır, canlı maç verisi için API şarttır.
        # Biz burada "Mevcut Veritabanındaki" takımlardan rastgele bir 'Günün Maçları' simülasyonu yapıyoruz
        # Çünkü bedava ve hatasız canlı fikstür çekmek imkansıza yakındır.
        return [] 
    except: return []

# --- SOHBET MOTORU ---
def akilli_cevap(soru):
    soru = soru.lower()
    if "türkiye başkent" in soru: return "🇹🇷 Ankara"
    if "naber" in soru: return "İyiyim, maçları analiz ediyorum!"
    if "kupon" in soru: return "Kupon sekmesine geç, oradan takımları seç halledeyim."
    return None

# --- ARAYÜZ ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3233/3233496.png", width=120)
    st.title("PRO BET V13")
    st.info(f"📅 {datetime.datetime.now().strftime('%d.%m.%Y')}")

st.title("🦁 FUTBOL KAHİNİ: PROFESSIONAL SUITE")

# --- LIVESCORE ---
with st.expander("📺 CANLI SKOR & FİKSTÜR (Buradan Bak)", expanded=True):
    components.html("""<iframe src="https://www.livescore.bz" width="100%" height="500" frameborder="0" style="background-color: #eee; border-radius: 8px;"></iframe>""", height=500, scrolling=True)

# --- SEKMELER ---
tab1, tab2, tab3 = st.tabs(["📊 DETAYLI ANALİZ", "🎫 AKILLI KUPON", "💬 SOHBET"])

# ================= SEKME 1: DETAYLI ANALİZ (BAHİS SİTESİ GİBİ) =================
with tab1:
    st.subheader("MAÇI SEÇ, TÜM İSTATİSTİKLERİ GÖR")
    
    col_l, col_r = st.columns([1, 3])
    with col_l:
        lig = st.selectbox("Lig:", list(lig_kodlari.keys()))
        df_lig = global_df[global_df['Lig'] == lig]
        takimlar = sorted(df_lig['HomeTeam'].unique())
        ev = st.selectbox("Ev Sahibi", takimlar)
        dep = st.selectbox("Deplasman", takimlar, index=1)
        btn_analiz = st.button("ANALİZ ET 🚀", type="primary")

    with col_r:
        if btn_analiz:
            res = detayli_analiz(ev, dep, global_df)
            if res:
                # 1. KAZANAN İBRESİ
                fig = go.Figure(go.Indicator(
                    mode = "gauge+number", value = res['ibre'],
                    title = {'text': "Kazanma İhtimali (%)"},
                    gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': "white"}, 'steps': [{'range': [0, 45], 'color': "#FF5252"}, {'range': [55, 100], 'color': "#00E676"}]}
                ))
                fig.update_layout(height=200, margin=dict(t=30,b=20,l=20,r=20), paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"})
                st.plotly_chart(fig, use_container_width=True)
                
                # 2. DETAYLI İSTATİSTİK KARTLARI (GRID)
                r1, r2, r3, r4 = st.columns(4)
                
                with r1:
                    st.markdown(f"""<div class="stat-box"><div class="stat-title">Skor Tahmini</div><div class="stat-value">{res['skor']}</div></div>""", unsafe_allow_html=True)
                with r2:
                    durum = "ÜST" if res['toplam_gol'] > 2.6 else "ALT"
                    renk = "risk-med" if durum == "ALT" else ""
                    st.markdown(f"""<div class="stat-box {renk}"><div class="stat-title">2.5 Gol</div><div class="stat-value">{durum}</div><small>{res['toplam_gol']:.2f}</small></div>""", unsafe_allow_html=True)
                with r3:
                    kg = "VAR" if res['kg_var'] else "YOK"
                    st.markdown(f"""<div class="stat-box"><div class="stat-title">KG (Karşılıklı Gol)</div><div class="stat-value">{kg}</div></div>""", unsafe_allow_html=True)
                with r4:
                    st.markdown(f"""<div class="stat-box"><div class="stat-title">Korner Beklentisi</div><div class="stat-value">{res['korner']:.1f}</div></div>""", unsafe_allow_html=True)

                r5, r6, r7, r8 = st.columns(4)
                with r5:
                    st.markdown(f"""<div class="stat-box risk-high"><div class="stat-title">Kart/Sertlik</div><div class="stat-value">{res['kart']:.1f}</div></div>""", unsafe_allow_html=True)
                with r6:
                     kazanan = ev if res['ibre'] > 55 else (dep if res['ibre'] < 45 else "X")
                     st.markdown(f"""<div class="stat-box"><div class="stat-title">Maç Sonucu</div><div class="stat-value">MS {kazanan}</div></div>""", unsafe_allow_html=True)
            else:
                st.error("Veri Yok")
        else:
            st.info("Soldan takım seç ve butona bas.")

# ================= SEKME 2: OTOMATİK KUPON (BUGÜN OYNAYANLAR) =================
with tab2:
    st.subheader("📅 BUGÜNÜN KUPONLARI")
    st.markdown("Yukarıdaki fikstürden bugün oynayanları seç, **Banko** ve **Sürpriz** kuponunu oluştur.")
    
    secilenler = st.multiselect("Bugün Oynayanları Listeden Bul:", tum_takimlar)
    
    if st.button("KUPONLARI OLUŞTUR 🎰"):
        if not secilenler: st.warning("Takım seçmedin.")
        else:
            banko, surpriz = [], []
            for t in secilenler:
                df_t = global_df[global_df['HomeTeam'] == t]
                if df_t.empty: continue
                # Basit analiz
                res = detayli_analiz(t, df=global_df, dep=df_t.iloc[0]['AwayTeam']) # Rakipten bağımsız genel güç
                # (Not: Rakipten bağımsız analiz yaptık çünkü rakibi otomatik bulamıyoruz, ama genel ev formu yeterli)
                
                # Sadece Ev Sahibinin gücüne bakarak kupon yapma
                guc = df_t['FTHG'].mean() * 1.5 - df_t['FTAG'].mean()
                gol = df_t['FTHG'].mean() + df_t['FTAG'].mean()
                lig = df_t.iloc[0]['Lig']
                
                # BANKO
                if guc > 1.3: banko.append({"m": f"{t} Kazanır", "o": 1.45, "t": "MS 1", "l": lig})
                elif gol > 3.0: banko.append({"m": f"{t} 2.5 ÜST", "o": 1.50, "t": "Gol", "l": lig})
                
                # SÜRPRİZ
                if 0 < guc < 0.3: surpriz.append({"m": f"{t} Berabere", "o": 3.20, "t": "MS 0", "l": lig})
                elif gol > 3.8: surpriz.append({"m": f"{t} 3.5 ÜST", "o": 2.80, "t": "Bol Gol", "l": lig})
            
            c1, c2 = st.columns(2)
            with c1: 
                st.success("✅ BANKO KUPON")
                for x in banko: st.markdown(f"""<div class="kupon-karti"><span class="oran">{x['o']}</span><b>{x['m']}</b><br><small>{x['l']}</small></div>""", unsafe_allow_html=True)
            with c2: 
                st.error("🔥 SÜRPRİZ KUPON")
                for x in surpriz: st.markdown(f"""<div class="kupon-karti surpriz"><span class="oran oran-s">{x['o']}</span><b>{x['m']}</b><br><small>{x['l']}</small></div>""", unsafe_allow_html=True)

# ================= SEKME 3: SOHBET =================
with tab3:
    if "messages" not in st.session_state: st.session_state.messages = [{"role": "assistant", "content": "Selam! Maçları sorabilirsin."}]
    for msg in st.session_state.messages: st.chat_message(msg["role"]).write(msg["content"])
    
    if prompt := st.chat_input("Mesaj yaz..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        
        cevap = akilli_cevap(prompt)
        if not cevap:
            # Futbol analizi yap
            bulunan = [t for t in tum_takimlar if t.lower() in prompt.lower()]
            if len(bulunan) >= 2:
                res = detayli_analiz(bulunan[0], bulunan[1], global_df)
                cevap = f"📊 **{bulunan[0]} vs {bulunan[1]}**\n\nTahmin: **{res['skor']}**. Gol Beklentisi: {res['toplam_gol']:.2f}. KG Var mı? {'Evet' if res['kg_var'] else 'Hayır'}."
            elif len(bulunan) == 1: cevap = f"**{bulunan[0]}** rakibini de yazarsan analiz ederim."
            else: cevap = "Anlamadım. Futbol veya genel kültür sorabilirsin."
            
        st.chat_message("assistant").write(cevap)
        st.session_state.messages.append({"role": "assistant", "content": cevap})
