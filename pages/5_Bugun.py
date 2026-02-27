"""
Bugün: Hangi programı yapacaksın seç; basit (tek ağırlık) veya detaylı (set set) giriş.

Detaylı modda her hareket için set sayısı kadar ağırlık girilir.
"""

import datetime

import streamlit as st

from auth import require_login
from components import inject_theme_css, render_sidebar
from config import WEEKDAYS
from db_operations import get_all_workouts, add_progress_log, get_pr
from utils.motivation import get_random_motivation


def main():
    require_login()
    inject_theme_css()
    with st.sidebar:
        render_sidebar("Bugün")
        st.markdown("---")

    today = datetime.date.today()
    today_str = today.isoformat()
    today_turkish = WEEKDAYS[today.weekday()]

    with st.container():
        st.title("📅 Bugün")
        st.markdown(f"**Tarih:** {today_str} ({today_turkish})")
        st.markdown("Hangi programı yapacaksın? Seç, ağırlıklarını gir (basit veya set set) ve kaydet.")
        st.caption(f"💬 {get_random_motivation()}")

    try:
        all_workouts = get_all_workouts()
    except Exception as e:
        st.error(f"Program yüklenirken hata: {e}")
        all_workouts = []

    selected_day = st.selectbox(
        "Hangi programı yapacaksın?",
        options=WEEKDAYS,
        index=WEEKDAYS.index(today_turkish) if today_turkish in WEEKDAYS else 0,
        key="bugun_day",
    )

    day_workouts = [w for w in all_workouts if w["day_name"] == selected_day]

    if not day_workouts:
        st.info(
            f"**{selected_day}** için programda hareket yok. "
            "Önce **Programım** sayfasından bu güne hareket ekle."
        )
        st.stop()

    # Basit vs Detaylı
    entry_mode = st.radio(
        "Giriş şekli",
        options=["Basit (tüm setler için tek ağırlık)", "Detaylı (her set için ayrı ağırlık)"],
        key="bugun_entry_mode",
    )
    detailed = "Detaylı" in entry_mode

    with st.form("bugun_agirlik_form"):
        st.subheader(f"{selected_day} – Ağırlık girişi (kg)")
        weights_by_exercise = {}

        for w in day_workouts:
            ex = w["exercise_name"]
            n_sets = int(w["sets"])
            reps = w["reps"]
            sets_reps = f"{n_sets} set x {reps} tekrar"

            if detailed:
                st.markdown(f"**{ex}** ({sets_reps})")
                set_weights = []
                for s in range(n_sets):
                    val = st.number_input(
                        f"Set {s+1} (kg)",
                        min_value=0.0,
                        value=0.0,
                        step=0.5,
                        key=f"weight_{w['id']}_set{s}",
                    )
                    set_weights.append(val)
                weights_by_exercise[ex] = set_weights
            else:
                weights_by_exercise[ex] = [
                    st.number_input(
                        f"{ex} ({sets_reps}) – kaldırdığın ağırlık (kg)",
                        min_value=0.0,
                        value=0.0,
                        step=0.5,
                        key=f"weight_{w['id']}",
                    )
                ]

        submitted = st.form_submit_button("Kaydet")

        if submitted:
            failed = []
            saved = 0
            new_prs = []
            db_error = None
            for ex, weight_list in weights_by_exercise.items():
                for kg in weight_list:
                    if kg <= 0:
                        continue
                    try:
                        prev_pr = get_pr(ex)
                        if prev_pr is not None and float(kg) > prev_pr:
                            new_prs.append(f"{ex} ({kg} kg)")
                        row_id = add_progress_log(today_str, ex, float(kg))
                        if row_id is not None:
                            saved += 1
                        else:
                            failed.append(ex)
                    except Exception as e:
                        failed.append(ex)
                        db_error = str(e)
            if db_error:
                st.error(f"Veritabanı hatası: {db_error}")
            if failed and not db_error:
                st.error(f"Bazı kayıtlar eklenemedi: {', '.join(set(failed))}")
            if saved:
                st.cache_data.clear()
                st.success(f"{saved} set/hareket için ağırlık kaydedildi.")
                if new_prs:
                    st.balloons()
                    st.success(f"🏆 Yeni kişisel rekor: {', '.join(new_prs)}")
                st.rerun()
            if saved == 0 and not failed:
                st.warning("En az bir set için 0'dan büyük ağırlık gir.")


if __name__ == "__main__":
    main()
