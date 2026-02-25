"""
Dashboard: Haftalık özet, protein serisi, interaktif Plotly grafik.

Grid: st.container + st.columns; veri st.cache_data ile önbellekli.
"""

import streamlit as st

from auth import require_login
from components import inject_theme_css, render_sidebar
from db_operations import (
    get_current_streak,
    get_total_weight_lifted_this_week,
    get_workout_count_this_week,
    get_weekly_totals,
)
from services.charts import build_weekly_weight_chart


def _safe_stats():
    """İstatistikleri güvenli şekilde döndürür; hata durumunda varsayılan."""
    try:
        streak = get_current_streak()
        total_weight = get_total_weight_lifted_this_week()
        workout_count = get_workout_count_this_week()
        return streak, total_weight, workout_count
    except Exception as e:
        st.error(f"İstatistikler yüklenirken hata: {e}")
        return 0, 0.0, 0


def main():
    require_login()
    inject_theme_css()
    with st.sidebar:
        render_sidebar("Dashboard")
        st.markdown("---")
        weeks_filter = st.slider("Grafik: son kaç hafta?", min_value=2, max_value=12, value=4)

    with st.container():
        st.title("📊 Dashboard")
        st.markdown("Bu haftanın özeti ve protein hedefi serin.")

    streak, total_weight, workout_count = _safe_stats()

    # Metrik kartları: grid (columns)
    col1, col2, col3 = st.columns(3)
    with col1:
        with st.container():
            st.markdown('<p class="card-title">🔥 Mevcut Seri (Protein Hedefi)</p>', unsafe_allow_html=True)
            st.metric(label="", value=f"{streak} Gün", delta=None)
    with col2:
        with st.container():
            st.markdown('<p class="card-title">Bu Hafta Toplam Kaldırılan Ağırlık</p>', unsafe_allow_html=True)
            st.metric(label="", value=f"{total_weight:.0f} kg", delta=None)
    with col3:
        with st.container():
            st.markdown('<p class="card-title">Bu Hafta Antrenman Sayısı</p>', unsafe_allow_html=True)
            st.metric(label="", value=str(workout_count), delta=None)

    st.markdown("---")

    # Plotly: haftalık toplam ağırlık
    with st.container():
        st.subheader("Haftalık Toplam Ağırlık (kg)")
        try:
            weekly_totals = get_weekly_totals(weeks=weeks_filter)
            fig = build_weekly_weight_chart(weekly_totals)
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Grafik oluşturulurken hata: {e}")

    with st.container():
        st.caption("Seri: Bugünden geriye doğru kesintisiz protein hedefini karşıladığın gün sayısı.")


if __name__ == "__main__":
    main()
