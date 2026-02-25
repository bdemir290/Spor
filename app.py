"""
Spor ve Beslenme Takip Uygulaması - Ana giriş dosyası.

Giriş ekranı (Admin / Misafir), koyu tema, mobil uyumlu kartlar.
"""

import streamlit as st

from auth import init_session_auth, is_logged_in, do_login, do_logout
from components import render_sidebar
from database import create_tables

# Sayfa yapılandırması
st.set_page_config(
    page_title="Spor ve Beslenme Takip",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_session_auth()

# Veritabanı tablolarını oluştur
try:
    create_tables()
except Exception:
    pass

# ---- Gri yazılar daha okunaklı; mobil uyumlu tema ----
STYLE = """
<style>
  /* Tema: gri yazılar açık (daha okunaklı) */
  :root {
    --bg-dark: #0e1117;
    --surface: #1a1d24;
    --surface-hover: #252930;
    --accent-green: #00e676;
    --accent-blue: #00b0ff;
    --text-primary: #f0f2f6;
    --text-muted: #d1d5db;
    --card-shadow: 0 4px 20px rgba(0, 230, 118, 0.08);
    --card-shadow-hover: 0 8px 32px rgba(0, 230, 118, 0.18);
  }

  .stApp { background: linear-gradient(180deg, #0e1117 0%, #1a1d24 100%); }
  [data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a1d24 0%, #0e1117 100%) !important;
  }
  [data-testid="stSidebar"] .stMarkdown { color: #f0f2f6; }

  /* Başlık ve açıklama - gri metin açık */
  h1, .main-title { color: var(--text-primary) !important; }
  .subtitle { color: var(--text-muted) !important; margin-bottom: 2rem; }
  p, .stMarkdown { color: var(--text-muted) !important; }
  [data-testid="stCaptionContainer"] { color: var(--text-muted) !important; }

  .nav-card { background: var(--surface); border: 1px solid rgba(0, 230, 118, 0.15);
    border-radius: 16px; padding: 1.5rem; margin-bottom: 1rem;
    box-shadow: var(--card-shadow); transition: all 0.3s ease; min-height: 140px; }
  .nav-card:hover { border-color: rgba(0, 230, 118, 0.4); box-shadow: var(--card-shadow-hover);
    transform: translateY(-4px); background: var(--surface-hover); }
  .nav-card-icon { font-size: 2.2rem; margin-bottom: 0.5rem; }
  .nav-card-title { color: var(--accent-green); font-weight: 700; font-size: 1.15rem; margin-bottom: 0.35rem; }
  .nav-card-desc { color: var(--text-muted); font-size: 0.9rem; line-height: 1.4; }

  [data-testid="stMetricValue"] { color: #00e676 !important; }
  [data-testid="stMetricLabel"] { color: var(--text-muted) !important; }
  .stButton > button {
    background: rgba(0, 230, 118, 0.2) !important; color: #00e676 !important;
    border: 1px solid rgba(0, 230, 118, 0.4) !important; border-radius: 8px !important;
    min-height: 2.5rem; padding: 0.5rem 1rem;
  }
  .stButton > button:hover { background: rgba(0, 230, 118, 0.3) !important; border-color: #00e676 !important; }

  .nav-card-wrapper a {
    display: inline-block !important; margin-top: 0.5rem !important;
    padding: 0.5rem 1rem !important; background: rgba(0, 230, 118, 0.15) !important;
    color: var(--accent-green) !important; border-radius: 8px !important;
    text-decoration: none !important; font-weight: 600 !important; font-size: 0.9rem !important;
    border: 1px solid rgba(0, 230, 118, 0.3) !important;
  }
  .nav-card-wrapper a:hover { background: rgba(0, 230, 118, 0.25) !important; color: var(--accent-green) !important; }

  /* Giriş kutusu */
  .login-box { max-width: 360px; margin: 2rem auto; padding: 2rem; }

  /* Mobil uyumluluk */
  @media (max-width: 768px) {
    .nav-card { min-height: 120px; padding: 1rem; }
    .nav-card-icon { font-size: 1.8rem; }
    .nav-card-title { font-size: 1rem; }
    .nav-card-desc { font-size: 0.85rem; }
    [data-testid="column"] { min-width: 100% !important; }
    .block-container { padding: 1rem !important; max-width: 100% !important; }
    .stButton > button { min-height: 3rem; font-size: 1rem; }
  }
  @media (max-width: 480px) {
    h1 { font-size: 1.5rem !important; }
    .subtitle { font-size: 0.95rem !important; }
  }
</style>
"""
st.markdown(STYLE, unsafe_allow_html=True)

# ---------- Giriş yapılmamışsa giriş ekranı ----------
if not is_logged_in():
    st.title("💪 Spor ve Beslenme Takip")
    st.markdown(
        '<p class="subtitle">Devam etmek için giriş yapın.</p>',
        unsafe_allow_html=True,
    )
    with st.form("giris_form"):
        kullanici = st.selectbox("Kullanıcı", options=["Admin", "Misafir"])
        parola = st.text_input("Parola", type="password", placeholder="Parolayı girin")
        giris = st.form_submit_button("Giriş Yap")
    if giris:
        if do_login(kullanici, parola):
            st.success(f"Hoş geldin, {kullanici}!")
            st.rerun()
        else:
            st.error("Kullanıcı adı veya parola hatalı.")
    st.stop()

# ---------- Giriş yapılmış: sidebar + çıkış ----------
with st.sidebar:
    st.caption(f"👤 {st.session_state.username}")
    if st.button("Çıkış Yap", use_container_width=True):
        do_logout()
        st.rerun()
    st.markdown("---")
    render_sidebar("Ana Sayfa")

# ---------- Ana sayfa içeriği ----------
st.title("💪 Spor ve Beslenme Takip")
st.markdown(
    '<p class="subtitle">Hedeflerini takip et, serini kırma, gelişimini gör.</p>',
    unsafe_allow_html=True,
)

st.subheader("Sayfalara git")
col1, col2, col3, col4 = st.columns(4)
PAGES = [
    ("📊", "Dashboard", "Özet ve zincir istatistikleri", "pages/1_Dashboard.py"),
    ("📋", "Programım", "Antrenman programı oluştur", "pages/2_Programim.py"),
    ("📈", "Gelişim", "Ağırlık takibi ve grafik", "pages/3_Gelisim.py"),
    ("🥗", "Beslenme", "Protein takibi ve takvim", "pages/4_Beslenme.py"),
]
for col, (icon, title, desc, path) in zip([col1, col2, col3, col4], PAGES):
    with col:
        st.markdown('<div class="nav-card-wrapper">', unsafe_allow_html=True)
        st.markdown(
            f'<div class="nav-card"><div class="nav-card-icon">{icon}</div>'
            f'<div class="nav-card-title">{title}</div><div class="nav-card-desc">{desc}</div></div>',
            unsafe_allow_html=True,
        )
        st.page_link(path, label=f"{title} →", icon=None)
        st.markdown("</div>", unsafe_allow_html=True)
