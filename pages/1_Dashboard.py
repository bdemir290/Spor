"""
Dashboard: Elite spor özeti – seri, haftalık hedef, PR, vücut ağırlığı, CSV export.

Bugünkü program hatırlatması, son antrenman, haftalık hedef çubuğu,
kişisel rekorlar, vücut ağırlığı girişi/grafik ve veri indirme.
"""

import datetime
import io

import streamlit as st
import pandas as pd

from auth import require_login
from components import inject_theme_css, render_sidebar
from config import WEEKDAYS
from db_operations import (
    get_current_streak,
    get_total_weight_lifted_this_week,
    get_workout_count_this_week,
    get_weekly_totals,
    get_pr,
    get_all_prs,
    get_last_workout_date,
    get_weekly_goal,
    set_weekly_goal,
    get_all_workouts,
    get_body_weight_logs,
    add_body_weight,
    get_progress_logs,
    get_nutrition_logs_all,
)
from services.charts import build_weekly_weight_chart, build_body_weight_chart
from utils.motivation import get_random_motivation


def _safe_stats():
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
        weekly_goal = st.number_input(
            "Haftalık antrenman hedefi",
            min_value=1,
            max_value=7,
            value=get_weekly_goal(),
            key="dashboard_weekly_goal",
        )
        if st.button("Hedefi Kaydet"):
            if set_weekly_goal(weekly_goal):
                st.cache_data.clear()
                st.success("Hedef kaydedildi.")
            else:
                st.error("Kaydedilemedi.")

    with st.container():
        st.title("📊 Dashboard")
        st.markdown("Elite spor takibi – haftalık özet, hedef ve kişisel rekorlar.")
        st.caption(f"💬 {get_random_motivation()}")

    today = datetime.date.today()
    today_turkish = WEEKDAYS[today.weekday()]

    # Bugünkü program hatırlatması
    try:
        all_workouts = get_all_workouts()
        today_workouts = [w for w in all_workouts if w["day_name"] == today_turkish]
        if today_workouts:
            with st.container():
                ex_list = ", ".join(w["exercise_name"] for w in today_workouts)
                st.info(f"**Bugünkü program ({today_turkish}):** {ex_list}")
        else:
            st.caption(f"Bugün ({today_turkish}) için program tanımlı değil.")
    except Exception:
        pass

    # Son antrenman
    try:
        last_date = get_last_workout_date()
        if last_date:
            last_d = datetime.datetime.strptime(last_date, "%Y-%m-%d").date()
            diff = (today - last_d).days
            if diff == 0:
                st.caption("Son antrenman: Bugün.")
            elif diff == 1:
                st.caption("Son antrenman: Dün.")
            else:
                st.caption(f"Son antrenman: {diff} gün önce.")
    except Exception:
        pass

    streak, total_weight, workout_count = _safe_stats()
    goal = get_weekly_goal()
    goal_progress = min(workout_count, goal)

    # Metrik kartları
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        with st.container():
            st.markdown('<p class="card-title">🔥 Protein serisi</p>', unsafe_allow_html=True)
            st.metric(label="", value=f"{streak} Gün", delta=None)
    with col2:
        with st.container():
            st.markdown('<p class="card-title">Bu hafta toplam (kg)</p>', unsafe_allow_html=True)
            st.metric(label="", value=f"{total_weight:.0f}", delta=None)
    with col3:
        with st.container():
            st.markdown('<p class="card-title">Antrenman (hedef)</p>', unsafe_allow_html=True)
            st.metric(label="", value=f"{workout_count} / {goal}", delta=None)
    with col4:
        prs = get_all_prs()
        with st.container():
            st.markdown('<p class="card-title">🏆 Kişisel rekor</p>', unsafe_allow_html=True)
            st.metric(label="", value=f"{len(prs)} hareket", delta=None)

    # Haftalık hedef çubuğu
    with st.container():
        st.markdown("**Haftalık hedef ilerleme**")
        st.progress(goal_progress / goal if goal else 0)
        st.caption(f"{workout_count} antrenman yapıldı, hedef {goal}.")

    st.markdown("---")

    # Haftalık toplam ağırlık grafiği
    with st.container():
        st.subheader("Haftalık toplam kaldırılan ağırlık (kg)")
        try:
            weekly_totals = get_weekly_totals(weeks=weeks_filter)
            fig = build_weekly_weight_chart(weekly_totals)
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Grafik oluşturulurken hata: {e}")

    # Vücut ağırlığı
    with st.container():
        st.subheader("Vücut ağırlığı (kg)")
        today_str = today.isoformat()
        c1, c2 = st.columns([1, 2])
        with c1:
            bw = st.number_input("Bugünkü ağırlık (kg)", min_value=30.0, max_value=200.0, value=70.0, step=0.1, key="body_weight_input")
            if st.button("Vücut ağırlığı kaydet"):
                if add_body_weight(today_str, float(bw)):
                    st.cache_data.clear()
                    st.success("Kaydedildi.")
                    st.rerun()
                else:
                    st.error("Kayıt eklenemedi.")
        with c2:
            try:
                bw_logs = get_body_weight_logs(90)
                if bw_logs:
                    bw_sorted = sorted(bw_logs, key=lambda x: x["date"])
                    fig_bw = build_body_weight_chart(bw_sorted)
                    st.plotly_chart(fig_bw, use_container_width=True)
                else:
                    st.caption("Henüz vücut ağırlığı kaydı yok. Soldan girip kaydet.")
            except Exception as e:
                st.error(f"Grafik hatası: {e}")

    st.markdown("---")

    # Kişisel rekorlar listesi
    prs_list = get_all_prs()
    if prs_list:
        with st.container():
            st.subheader("🏆 Kişisel rekorlar")
            df_pr = pd.DataFrame(prs_list)
            st.dataframe(df_pr, column_config={"exercise_name": "Hareket", "pr_kg": "Rekor (kg)"}, hide_index=True, use_container_width=True)

    st.markdown("---")

    # Veri dışa aktarma (CSV)
    with st.container():
        st.subheader("Verileri indir (CSV)")
        try:
            progress = get_progress_logs()
            nutrition = get_nutrition_logs_all()
            if progress:
                df_p = pd.DataFrame(progress)
                buf = io.StringIO()
                df_p.to_csv(buf, index=False)
                st.download_button("Antrenman geçmişi (CSV)", data=buf.getvalue(), file_name="antrenman_gecmisi.csv", mime="text/csv", key="dl_progress")
            if nutrition:
                df_n = pd.DataFrame(nutrition)
                buf_n = io.StringIO()
                df_n.to_csv(buf_n, index=False)
                st.download_button("Beslenme kayıtları (CSV)", data=buf_n.getvalue(), file_name="beslenme_kayitlari.csv", mime="text/csv", key="dl_nutrition")
            if not progress and not nutrition:
                st.caption("Henüz dışa aktarılacak veri yok.")
        except Exception as e:
            st.error(f"İndirme hatası: {e}")

    with st.container():
        st.caption("Seri: Bugünden geriye doğru kesintisiz protein hedefini karşıladığın gün sayısı.")


if __name__ == "__main__":
    main()
