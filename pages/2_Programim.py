"""
Programım: Antrenman programı ekleme, listeleme, silme.

Kurumsal card layout; gün filtresi; try-except ile anlamlı hata mesajları.
Yazma sonrası st.cache_data.clear() ile önbellek güncellenir.
"""

import streamlit as st
import pandas as pd

from auth import require_login
from components import inject_theme_css, render_sidebar
from config import WEEKDAYS
from db_operations import add_workout, get_all_workouts, delete_workout
from utils.motivation import get_random_motivation


def main():
    require_login()
    inject_theme_css()
    with st.sidebar:
        render_sidebar("Programım")
        st.markdown("---")
        filter_day = st.selectbox(
            "Filtre: Gün",
            options=["Tümü"] + WEEKDAYS,
            key="program_filter_day",
        )

    with st.container():
        st.title("📋 Programım")
        st.markdown("Antrenman programına hareket ekleyebilir veya silebilirsin.")
        st.caption(f"💬 {get_random_motivation()}")

    # Form: yeni hareket
    with st.container():
        with st.form("yeni_hareket_form", clear_on_submit=True):
            st.subheader("Yeni Hareket Ekle")
            c1, c2, c3 = st.columns(3)
            with c1:
                day_name = st.selectbox("Gün", options=WEEKDAYS, index=0)
            with c2:
                exercise_name = st.text_input("Hareket Adı", placeholder="Örn: Bench Press")
            with c3:
                sets = st.number_input("Set", min_value=1, max_value=20, value=3)
            reps = st.number_input("Tekrar", min_value=1, max_value=100, value=10, key="reps_input")
            submitted = st.form_submit_button("Ekle")

            if submitted:
                ex_clean = (exercise_name or "").strip()
                if not ex_clean:
                    st.error("Hareket adı boş bırakılamaz. Lütfen bir isim girin.")
                else:
                    try:
                        row_id = add_workout(
                            day_name=day_name,
                            exercise_name=ex_clean,
                            sets=int(sets),
                            reps=int(reps),
                        )
                        if row_id is not None:
                            st.cache_data.clear()
                            st.success("Hareket programına eklendi.")
                            st.rerun()
                        else:
                            st.error("Veritabanına eklenirken bir hata oluştu. Lütfen tekrar dene.")
                    except Exception as e:
                        st.error(f"Beklenmeyen hata: {e}")

    st.markdown("---")

    # Mevcut program (filtre uygulanmış)
    with st.container():
        st.subheader("Mevcut Program")
        try:
            workouts = get_all_workouts()
        except Exception as e:
            st.error(f"Program yüklenirken hata: {e}")
            workouts = []

        if filter_day != "Tümü":
            workouts = [w for w in workouts if w["day_name"] == filter_day]

        if not workouts:
            st.info("Bu filtrede veya programda hareket yok. Yukarıdaki formdan ekleyebilirsin.")
        else:
            df = pd.DataFrame(workouts)
            df = df[["day_name", "exercise_name", "sets", "reps"]]
            df.columns = ["Gün", "Hareket", "Set", "Tekrar"]
            st.dataframe(df, use_container_width=True, hide_index=True)

            st.markdown("#### Hareket Sil")
            ids = [w["id"] for w in workouts]
            labels = [
                f"{w['day_name']} – {w['exercise_name']} ({w['sets']}x{w['reps']})"
                for w in workouts
            ]
            choice = st.selectbox(
                "Silmek istediğin hareketi seç",
                range(len(ids)),
                format_func=lambda i: labels[i],
                key="delete_choice",
            )
            if st.button("Seçileni Sil"):
                try:
                    ok = delete_workout(ids[choice])
                    if ok:
                        st.cache_data.clear()
                        st.success("Kayıt silindi.")
                        st.rerun()
                    else:
                        st.warning("Silme işlemi başarısız; kayıt bulunamadı olabilir.")
                except Exception as e:
                    st.error(f"Silme sırasında hata: {e}")


if __name__ == "__main__":
    main()
