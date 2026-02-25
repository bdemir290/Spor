"""
Dashboard sayfası: Haftalık özet ve zinciri kırma (streak) istatistikleri.

Veritabanından bu haftanın verileri çekilir; protein serisi ve
toplam ağırlık/antrenman sayısı gösterilir.
"""

import streamlit as st

from auth import require_login
from components import inject_theme_css, render_sidebar
from db_operations import (
    get_current_streak,
    get_total_weight_lifted_this_week,
    get_workout_count_this_week,
)


def main():
    require_login()
    inject_theme_css()
    with st.sidebar:
        render_sidebar("Dashboard")
    st.title("📊 Dashboard")
    st.markdown("Bu haftanın özeti ve protein hedefi serin.")

    try:
        streak = get_current_streak()
        total_weight = get_total_weight_lifted_this_week()
        workout_count = get_workout_count_this_week()
    except Exception:
        streak = 0
        total_weight = 0.0
        workout_count = 0

    # Zinciri kırma (streak) - büyük metrik
    st.metric(
        label="🔥 Mevcut Seri (Protein Hedefi)",
        value=f"{streak} Gün",
        delta=None,
    )

    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            label="Bu Hafta Toplam Kaldırılan Ağırlık",
            value=f"{total_weight:.0f} kg",
            delta=None,
        )
    with col2:
        st.metric(
            label="Bu Hafta Antrenman Sayısı",
            value=str(workout_count),
            delta=None,
        )

    st.markdown("---")
    st.caption("Seri: Bugünden geriye doğru kesintisiz protein hedefini karşıladığın gün sayısı.")


if __name__ == "__main__":
    main()
