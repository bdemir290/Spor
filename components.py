"""
Ortak UI bileşenleri: sidebar menü ve tema CSS.

Tüm sayfalarda aynı koyu tema ve sayfa linkleri için kullanılır.
"""

import streamlit as st

# Sayfa listesi: (etiket, ikon, sayfa yolu)
PAGE_OPTIONS = [
    ("Ana Sayfa", "🏠", "app.py"),
    ("Dashboard", "📊", "pages/1_Dashboard.py"),
    ("Programım", "📋", "pages/2_Programim.py"),
    ("Gelişim", "📈", "pages/3_Gelisim.py"),
    ("Beslenme", "🥗", "pages/4_Beslenme.py"),
]


def render_sidebar(current_page: str = "", show_logout: bool = True) -> None:
    """
    Sidebar'da kullanıcı (giriş yapılmışsa), çıkış butonu ve sayfa linkleri çizer.

    Args:
        current_page: Uyumluluk için bırakıldı.
        show_logout: True ise kullanıcı adı ve Çıkış Yap butonu gösterilir.
    """
    try:
        from auth import is_logged_in, do_logout
        if show_logout and is_logged_in():
            st.sidebar.caption(f"👤 {st.session_state.get('username', '')}")
            if st.sidebar.button("Çıkış Yap", use_container_width=True, key="sidebar_logout"):
                do_logout()
                st.switch_page("app.py")
            st.sidebar.markdown("---")
    except Exception:
        pass
    st.sidebar.markdown("")
    for label, icon, path in PAGE_OPTIONS:
        st.sidebar.page_link(path, label=label, icon=icon)


def inject_theme_css() -> None:
    """Koyu tema, spor paleti; gri yazılar açık ton, mobil uyumlu."""
    st.markdown(
        """
    <style>
      :root {
        --bg-dark: #0e1117;
        --surface: #1a1d24;
        --accent-green: #00e676;
        --accent-blue: #00b0ff;
        --text-primary: #f0f2f6;
        --text-muted: #d1d5db;
      }
      .stApp { background: linear-gradient(180deg, #0e1117 0%, #1a1d24 100%); }
      [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1d24 0%, #0e1117 100%) !important;
      }
      p, .stMarkdown, [data-testid="stCaptionContainer"] { color: var(--text-muted) !important; }
      [data-testid="stMetricValue"] { color: #00e676 !important; }
      [data-testid="stMetricLabel"] { color: var(--text-muted) !important; }
      .stButton > button {
        background: rgba(0, 230, 118, 0.2) !important;
        color: #00e676 !important;
        border: 1px solid rgba(0, 230, 118, 0.4) !important;
        border-radius: 8px !important;
        min-height: 2.5rem; padding: 0.5rem 1rem;
      }
      .stButton > button:hover {
        background: rgba(0, 230, 118, 0.3) !important;
        border-color: #00e676 !important;
      }
      @media (max-width: 768px) {
        .block-container { padding: 1rem !important; max-width: 100% !important; }
        .stButton > button { min-height: 3rem; font-size: 1rem; }
      }
    </style>
    """,
        unsafe_allow_html=True,
    )
