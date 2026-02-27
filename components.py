"""
Ortak UI bileşenleri: sidebar, tema, kurumsal card layout.

Tüm sayfalarda tutarlı grid ve container yapısı için kullanılır.
"""

import streamlit as st

from config import THEME_CSS

PAGE_OPTIONS = [
    ("Ana Sayfa", "🏠", "app.py"),
    ("Bugün", "📅", "pages/5_Bugun.py"),
    ("Dashboard", "📊", "pages/1_Dashboard.py"),
    ("Programım", "📋", "pages/2_Programim.py"),
    ("Gelişim", "📈", "pages/3_Gelisim.py"),
    ("Beslenme", "🥗", "pages/4_Beslenme.py"),
]


def get_theme_css() -> str:
    """Kurumsal tema CSS metnini döndürür."""
    return THEME_CSS


def inject_theme_css() -> None:
    """Sayfaya tema CSS'ini enjekte eder."""
    st.markdown(get_theme_css(), unsafe_allow_html=True)


def render_sidebar(current_page: str = "", show_logout: bool = False) -> None:
    """Sidebar: geri tuşu ve sayfa linkleri (giriş/çıkış kapalı, show_logout varsayılan False)."""
    try:
        if show_logout:
            from auth import is_logged_in, do_logout
            if is_logged_in():
                st.sidebar.caption(f"👤 {st.session_state.get('username', '')}")
                if st.sidebar.button("Çıkış Yap", use_container_width=True, key="sidebar_logout"):
                    do_logout()
                    st.switch_page("app.py")
                st.sidebar.markdown("---")
    except Exception:
        pass
    # Alt sayfalardan ana sayfaya dönmek için geri tuşu
    if current_page and current_page != "Ana Sayfa":
        if st.sidebar.button("← Ana Sayfaya Dön", use_container_width=True, key="sidebar_back"):
            st.switch_page("app.py")
        st.sidebar.markdown("")
    for label, icon, path in PAGE_OPTIONS:
        st.sidebar.page_link(path, label=label, icon=icon)


def card_container(title: str = "", key: str = None):
    """
    Kurumsal card görünümlü bir st.container döndürür.
    İçeriği grid içinde düzenlemek için with card_container(...): kullanın.

    Args:
        title: Kart başlığı (opsiyonel).
        key: Streamlit container key (opsiyonel).
    """
    cont = st.container(key=key)
    with cont:
        if title:
            st.markdown(
                f'<p class="card-title">{title}</p>',
                unsafe_allow_html=True,
            )
    return cont


def render_metric_card(label: str, value: str, delta: str = None, container=None):
    """
    Metrik değerini card layout içinde gösterir.

    Args:
        label: Metrik etiketi.
        value: Ana değer.
        delta: Değişim (opsiyonel).
        container: st.container veya None (yeni container açılır).
    """
    target = container or st.container()
    with target:
        st.markdown(f'<p class="card-title">{label}</p>', unsafe_allow_html=True)
        st.metric(label="", value=value, delta=delta)
