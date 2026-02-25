"""
Programım sayfası: Antrenman programı oluşturma, listeleme ve silme.

Kullanıcı gün, hareket adı, set ve tekrar girebilir;
eklenen program tablo olarak gösterilir ve istenen hareket silinebilir.
"""

import streamlit as st

from auth import require_login
from components import inject_theme_css, render_sidebar
from db_operations import add_workout, get_all_workouts, delete_workout


def main():
    require_login()
    inject_theme_css()
    with st.sidebar:
        render_sidebar("Programım")
    st.title("📋 Programım")
    st.markdown("Antrenman programına hareket ekleyebilir veya silebilirsin.")

    # Form ile yeni hareket ekleme
    with st.form("yeni_hareket_form", clear_on_submit=True):
        st.subheader("Yeni Hareket Ekle")
        day_name = st.selectbox(
            "Gün",
            options=[
                "Pazartesi",
                "Salı",
                "Çarşamba",
                "Perşembe",
                "Cuma",
                "Cumartesi",
                "Pazar",
            ],
            index=0,
        )
        exercise_name = st.text_input("Hareket Adı", placeholder="Örn: Bench Press")
        sets = st.number_input("Set", min_value=1, max_value=20, value=3)
        reps = st.number_input("Tekrar", min_value=1, max_value=100, value=10)
        submitted = st.form_submit_button("Ekle")

        if submitted:
            if not (exercise_name and exercise_name.strip()):
                st.error("Hareket adı boş bırakılamaz.")
            else:
                try:
                    row_id = add_workout(
                        day_name=day_name,
                        exercise_name=exercise_name.strip(),
                        sets=int(sets),
                        reps=int(reps),
                    )
                    if row_id is not None:
                        st.success("Hareket programına eklendi.")
                    else:
                        st.error("Eklenirken bir hata oluştu.")
                except Exception:
                    st.error("Eklenirken bir hata oluştu.")

    st.markdown("---")
    st.subheader("Mevcut Program")

    try:
        workouts = get_all_workouts()
    except Exception:
        workouts = []

    if not workouts:
        st.info("Henüz programda hareket yok. Yukarıdaki formdan ekleyebilirsin.")
    else:
        # Tablo olarak göster (st.dataframe ile düzenlenebilir değil, sadece görüntüleme)
        import pandas as pd
        df = pd.DataFrame(workouts)
        df = df[["day_name", "exercise_name", "sets", "reps"]]
        df.columns = ["Gün", "Hareket", "Set", "Tekrar"]
        st.dataframe(df, use_container_width=True, hide_index=True)

        # Silme: id'ye göre sil
        st.markdown("#### Hareket Sil")
        ids = [w["id"] for w in workouts]
        labels = [
            f"{w['day_name']} - {w['exercise_name']} ({w['sets']}x{w['reps']})"
            for w in workouts
        ]
        choice = st.selectbox(
            "Silmek istediğin hareketi seç",
            range(len(ids)),
            format_func=lambda i: labels[i],
        )
        if st.button("Seçileni Sil"):
            try:
                ok = delete_workout(ids[choice])
                if ok:
                    st.success("Kayıt silindi. Sayfayı yenile.")
                    st.rerun()
                else:
                    st.warning("Silme işlemi başarısız.")
            except Exception:
                st.error("Silme sırasında hata oluştu.")


if __name__ == "__main__":
    main()
