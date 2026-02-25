"""
Giriş modülü: Kullanıcı doğrulama ve oturum kontrolü.

Admin ve Misafir hesapları tanımlıdır; parola doğrulama
Streamlit session_state ile yönetilir.
"""

import streamlit as st

# Kullanıcı adı -> parola (gerçek uygulamada şifrelenmiş saklanır)
USERS = {
    "Admin": "Demir3429",
    "Misafir": "12345",
}


def init_session_auth() -> None:
    """Oturum için giriş bilgilerini session_state'te başlatır."""
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "username" not in st.session_state:
        st.session_state.username = None


def check_login(username: str, password: str) -> bool:
    """
    Kullanıcı adı ve parolayı kontrol eder.

    Args:
        username: Kullanıcı adı (Admin veya Misafir).
        password: Parola.

    Returns:
        Doğruysa True, değilse False.
    """
    if not username or not password:
        return False
    return USERS.get(username.strip()) == password


def is_logged_in() -> bool:
    """Kullanıcının giriş yapıp yapmadığını döndürür."""
    init_session_auth()
    return bool(st.session_state.logged_in)


def do_login(username: str, password: str) -> bool:
    """Giriş yapar; başarılıysa session_state güncellenir."""
    if check_login(username, password):
        st.session_state.logged_in = True
        st.session_state.username = username.strip()
        return True
    return False


def do_logout() -> None:
    """Çıkış yapar."""
    st.session_state.logged_in = False
    st.session_state.username = None


def require_login() -> bool:
    """
    Sayfa giriş gerektiriyorsa True döner; giriş yoksa
    ana sayfaya yönlendirir ve False döner.
    """
    init_session_auth()
    if not st.session_state.logged_in:
        st.switch_page("app.py")
        return False
    return True
