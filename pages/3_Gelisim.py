"""
Gelişim sayfası: Ağırlık takibi, yüzdelik artış ve zaman serisi grafiği.

Kullanıcı hareket seçer, tarih ve kaldırdığı ağırlığı girer.
Son iki ağırlığa göre yüzde değişim hesaplanıp st.metric ile gösterilir.
Hareketin zaman içindeki gelişimi st.line_chart ile çizilir.
"""

import streamlit as st
import pandas as pd

from auth import require_login
from components import inject_theme_css, render_sidebar
from db_operations import (
    add_progress_log,
    get_progress_logs,
    get_all_workouts,
    get_distinct_exercises_from_progress,
)


def main():
    require_login()
    inject_theme_css()
    with st.sidebar:
        render_sidebar("Gelişim")
    st.title("📈 Haftalık Gelişim")
    st.markdown("Ağırlık girişi yap, yüzde artışını gör ve grafiği incele.")

    # Hareket listesi: programdaki + geçmişte kullanılan
    try:
        from_workouts = [w["exercise_name"] for w in get_all_workouts()]
        from_progress = get_distinct_exercises_from_progress()
        all_exercises = sorted(set(from_workouts) | set(from_progress))
    except Exception:
        all_exercises = []

    if not all_exercises:
        all_exercises = ["Bench Press", "Squat", "Deadlift"]

    # Form: tarih, hareket, ağırlık
    with st.form("agirlik_form", clear_on_submit=True):
        st.subheader("Yeni Ağırlık Girişi")
        exercise_name = st.selectbox("Hareket", options=all_exercises)
        date_str = st.date_input("Tarih").isoformat()
        weight = st.number_input("Kaldırılan Ağırlık (kg)", min_value=0.1, value=50.0, step=0.5)
        submitted = st.form_submit_button("Kaydet")

        if submitted:
            try:
                row_id = add_progress_log(
                    date=date_str,
                    exercise_name=exercise_name,
                    weight_lifted=weight,
                )
                if row_id is not None:
                    st.success("Kayıt eklendi.")
                else:
                    st.error("Kayıt eklenirken hata oluştu.")
            except Exception:
                st.error("Kayıt eklenirken hata oluştu.")

    st.markdown("---")
    st.subheader("Hareket Gelişimi")

    selected = st.selectbox(
        "Grafik ve metrik için hareket seç",
        options=all_exercises,
        key="gelisim_secim",
    )

    try:
        logs = get_progress_logs(selected)
    except Exception:
        logs = []

    if not logs:
        st.info("Bu hareket için henüz kayıt yok. Yukarıdan giriş yapabilirsin.")
    else:
        # Son iki ağırlık ile yüzde değişim
        weights = [r["weight_lifted"] for r in logs]
        dates_sorted = [r["date"] for r in logs]
        # Tarih sırasına göre (zaten get_progress_logs ORDER BY date ASC)
        last_two = weights[-2:] if len(weights) >= 2 else weights
        if len(last_two) == 2:
            old_w, new_w = last_two[0], last_two[1]
            if old_w > 0:
                pct = ((new_w - old_w) / old_w) * 100
                delta_str = f"%{pct:+.1f} Değişim"
            else:
                delta_str = "—"
            value_str = f"{new_w} kg"
        else:
            value_str = f"{weights[-1]} kg"
            delta_str = "—"

        st.metric(
            label=selected,
            value=value_str,
            delta=delta_str,
        )

        # Zaman serisi grafiği
        df = pd.DataFrame(logs)
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date")
        chart_df = df[["date", "weight_lifted"]].set_index("date")
        chart_df.columns = ["Ağırlık (kg)"]
        st.line_chart(chart_df)


if __name__ == "__main__":
    main()
