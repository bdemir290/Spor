"""
Spor ve Beslenme Takip – Ana giriş.

Giriş ekranı, kurumsal card layout, grid sistemi.
Modüler yapı: config (tema), components (sidebar, card), auth.
"""

import streamlit as st

from auth import init_session_auth, is_logged_in, do_login, do_logout
from components import render_sidebar
from config import THEME_CSS
from database import create_tables

st.set_page_config(
    page_title="Spor ve Beslenme Takip",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_session_auth()

# Veritabanı: tabloları oluştur; hata durumunda anlamlı geri bildirim
try:
    create_tables()
except Exception as e:
    st.error(f"Veritabanı başlatılamadı: {e}. Lütfen uygulama dizinini kontrol edin.")

# Tema CSS (tek kaynak: config)
st.markdown(THEME_CSS, unsafe_allow_html=True)

# ---------- Giriş yapılmamışsa: giriş formu (container ile) ----------
if not is_logged_in():
    with st.container():
        st.title("💪 Spor ve Beslenme Takip")
        st.markdown(
            '<p class="subtitle">Devam etmek için giriş yapın.</p>',
            unsafe_allow_html=True,
        )
    with st.container():
        with st.form("giris_form"):
            kullanici = st.selectbox("Kullanıcı", options=["Admin", "Misafir"])
            parola = st.text_input("Parola", type="password", placeholder="Parolayı girin")
            giris = st.form_submit_button("Giriş Yap")
        if giris:
            if not parola or not parola.strip():
                st.error("Parola boş bırakılamaz.")
            elif do_login(kullanici, parola):
                st.success(f"Hoş geldin, {kullanici}!")
                st.rerun()
            else:
                st.error("Kullanıcı adı veya parola hatalı. Lütfen tekrar deneyin.")
    st.stop()

# ---------- Giriş yapılmış: sidebar + ana içerik grid ----------
with st.sidebar:
    st.caption(f"👤 {st.session_state.username}")
    if st.button("Çıkış Yap", use_container_width=True):
        do_logout()
        st.rerun()
    st.markdown("---")
    render_sidebar("Ana Sayfa")

# Ana sayfa: başlık + kart grid (st.columns + container)
with st.container():
    st.title("💪 Spor ve Beslenme Takip")
    st.markdown(
        '<p class="subtitle">Hedeflerini takip et, serini kırma, gelişimini gör.</p>',
        unsafe_allow_html=True,
    )

with st.container():
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
