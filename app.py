"""
Spor ve Beslenme Takip – Ana giriş.

Giriş ekranı, kurumsal card layout, grid sistemi.
Modüler yapı: config (tema), components (sidebar, card), auth.
"""

import streamlit as st

from auth import init_session_auth
from components import render_sidebar
from config import THEME_CSS
from database import create_tables, get_db_path
from utils.motivation import get_random_motivation

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

# Sidebar + ana içerik (giriş/şifre yok)
with st.sidebar:
    with st.expander("Veritabanı konumu"):
        db_path = get_db_path()
        st.code(db_path, language=None)
        import os
        if os.path.isfile(db_path):
            try:
                size = os.path.getsize(db_path)
                st.caption(f"Dosya mevcut ({size} byte). Kayıtlar burada tutuluyor.")
            except Exception:
                st.caption("Dosya mevcut.")
        else:
            st.caption("İlk kayıtta oluşturulacak. Kayıt çalışmıyorsa bu klasörün yazılabilir olduğundan emin olun.")
    st.markdown("---")
    render_sidebar("Ana Sayfa")

# Ana sayfa: başlık + kart grid (st.columns + container)
with st.container():
    st.title("💪 Spor ve Beslenme Takip")
    st.markdown(
        '<p class="subtitle">Hedeflerini takip et, serini kırma, gelişimini gör.</p>',
        unsafe_allow_html=True,
    )
    st.caption(f"💬 {get_random_motivation()}")

with st.container():
    st.subheader("Sayfalara git")
    col1, col2, col3, col4, col5 = st.columns(5)
    PAGES = [
        ("📅", "Bugün", "Bugünkü programı seç, ağırlıkları gir", "pages/5_Bugun.py"),
        ("📊", "Dashboard", "Özet ve zincir istatistikleri", "pages/1_Dashboard.py"),
        ("📋", "Programım", "Antrenman programı oluştur", "pages/2_Programim.py"),
        ("📈", "Gelişim", "Ağırlık takibi ve grafik", "pages/3_Gelisim.py"),
        ("🥗", "Beslenme", "Protein ve vitamin takibi", "pages/4_Beslenme.py"),
    ]
    for col, (icon, title, desc, path) in zip([col1, col2, col3, col4, col5], PAGES):
        with col:
            st.markdown('<div class="nav-card-wrapper">', unsafe_allow_html=True)
            st.markdown(
                f'<div class="nav-card"><div class="nav-card-icon">{icon}</div>'
                f'<div class="nav-card-title">{title}</div><div class="nav-card-desc">{desc}</div></div>',
                unsafe_allow_html=True,
            )
            st.page_link(path, label=f"{title} →", icon=None)
            st.markdown("</div>", unsafe_allow_html=True)
