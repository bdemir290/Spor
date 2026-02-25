"""
Gelişim: Ağırlık girişi, yüzde değişim metrik, Plotly çizgi grafik.

Hareket ve tarih filtreleri; try-except ve st.error ile hata geri bildirimi.
"""

import streamlit as st
import pandas as pd

from auth import require_login
from components import inject_theme_css, render_sidebar
from config import DEFAULT_EXERCISES
from db_operations import (
    add_progress_log,
    get_progress_logs,
    get_all_workouts,
    get_distinct_exercises_from_progress,
)
from services.charts import build_progress_line_chart


def _all_exercises():
    """Program + geçmişte kullanılan hareketlerin birleşimi."""
    try:
        from_workouts = [w["exercise_name"] for w in get_all_workouts()]
        from_progress = get_distinct_exercises_from_progress()
        return sorted(set(from_workouts) | set(from_progress))
    except Exception:
        return DEFAULT_EXERCISES


def main():
    require_login()
    inject_theme_css()
    with st.sidebar:
        render_sidebar("Gelişim")
        st.markdown("---")

    all_exercises = _all_exercises()

    with st.container():
        st.title("📈 Haftalık Gelişim")
        st.markdown("Ağırlık girişi yap, yüzde artışını gör ve grafiği incele.")

    # Form: yeni ağırlık
    with st.container():
        with st.form("agirlik_form", clear_on_submit=True):
            st.subheader("Yeni Ağırlık Girişi")
            c1, c2, c3 = st.columns(3)
            with c1:
                exercise_name = st.selectbox("Hareket", options=all_exercises, key="form_exercise")
            with c2:
                date_val = st.date_input("Tarih", key="form_date")
            with c3:
                weight = st.number_input("Kaldırılan Ağırlık (kg)", min_value=0.1, value=50.0, step=0.5, key="form_weight")
            submitted = st.form_submit_button("Kaydet")

            if submitted:
                try:
                    date_str = date_val.isoformat()
                    if weight <= 0:
                        st.error("Ağırlık 0'dan büyük olmalıdır.")
                    else:
                        row_id = add_progress_log(
                            date=date_str,
                            exercise_name=exercise_name,
                            weight_lifted=float(weight),
                        )
                        if row_id is not None:
                            st.cache_data.clear()
                            st.success("Kayıt eklendi.")
                            st.rerun()
                        else:
                            st.error("Kayıt eklenirken veritabanı hatası oluştu.")
                except Exception as e:
                    st.error(f"Kayıt eklenirken hata: {e}")

    st.markdown("---")

    # Grafik ve metrik: hareket seçimi
    with st.container():
        st.subheader("Hareket Gelişimi")
        selected = st.selectbox(
            "Grafik ve metrik için hareket seç",
            options=all_exercises,
            key="gelisim_secim",
        )

    try:
        logs = get_progress_logs(selected)
    except Exception as e:
        st.error(f"Veri yüklenirken hata: {e}")
        logs = []

    if not logs:
        st.info("Bu hareket için henüz kayıt yok. Yukarıdan giriş yapabilirsin.")
    else:
        weights = [r["weight_lifted"] for r in logs]
        dates = [r["date"] for r in logs]
        last_two = weights[-2:] if len(weights) >= 2 else weights

        with st.container():
            if len(last_two) == 2 and last_two[0] > 0:
                pct = ((last_two[1] - last_two[0]) / last_two[0]) * 100
                delta_str = f"%{pct:+.1f} Değişim"
            else:
                delta_str = None
            st.metric(label=selected, value=f"{weights[-1]} kg", delta=delta_str)

        with st.container():
            try:
                fig = build_progress_line_chart(dates, weights, selected)
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Grafik oluşturulurken hata: {e}")


if __name__ == "__main__":
    main()
