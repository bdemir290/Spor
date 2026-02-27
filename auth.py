"""
Oturum modülü: Şifre kapatıldı, uygulama tek kullanıcı için doğrudan açılır.
"""

import streamlit as st


def init_session_auth() -> None:
    """Oturum bilgilerini session_state'te başlatır (giriş zorunlu değil)."""
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = True
    if "username" not in st.session_state:
        st.session_state.username = "Kullanıcı"


def is_logged_in() -> bool:
    """Her zaman True – giriş ekranı kullanılmıyor."""
    init_session_auth()
    return True


def do_logout() -> None:
    """Şifre kapatıldığı için boş (çıkış yok)."""
    pass


def require_login() -> bool:
    """Giriş zorunlu değil; her zaman True döner."""
    init_session_auth()
    return True
