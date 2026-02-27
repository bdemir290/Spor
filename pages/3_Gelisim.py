"""
Gelişim: Ağırlık + tekrar girişi, tahmini 1RM, volume, grafikler.
Tekrar dikkate alan özet (Epley 1RM, volume). Her sayfada rastgele motivasyon cümlesi.
"""

import streamlit as st
import pandas as pd

from auth import require_login
from components import inject_theme_css, render_sidebar
from config import DEFAULT_EXERCISES
from db_operations import (
    add_progress_log,
    get_progress_logs,
    get_progress_logs_aggregated,
    get_all_workouts,
    get_distinct_exercises_from_progress,
)
from services.charts import build_progress_line_chart, build_1rm_line_chart
from utils.motivation import get_random_motivation


def _all_exercises():
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

    st.caption(f"💬 {get_random_motivation()}")

    all_exercises = _all_exercises()

    with st.container():
        st.title("📈 Haftalık Gelişim")
        st.markdown("Ağırlık ve tekrar gir (basit veya set set); tahmini 1RM ve volume takip edilir.")

    # Form: ağırlık + tekrar (basit veya detaylı)
    with st.container():
        with st.form("agirlik_form", clear_on_submit=True):
            st.subheader("Yeni Ağırlık Girişi")
            entry_mode = st.radio(
                "Giriş şekli",
                options=["Basit (tek ağırlık + tekrar)", "Detaylı (her set için ağırlık + tekrar)"],
                key="gelisim_entry_mode",
            )
            detailed = "Detaylı" in entry_mode

            c1, c2 = st.columns(2)
            with c1:
                exercise_name = st.selectbox("Hareket", options=all_exercises, key="form_exercise")
            with c2:
                date_val = st.date_input("Tarih", key="form_date")

            if detailed:
                n_sets = st.number_input("Kaç set?", min_value=1, max_value=10, value=3, key="form_n_sets")
                st.caption("Her set için ağırlık (kg) ve tekrar sayısını gir. 0 olan setler kaydedilmez.")
                set_weights = []
                set_reps = []
                for s in range(int(n_sets)):
                    col_w, col_r = st.columns(2)
                    with col_w:
                        set_weights.append(
                            st.number_input(f"Set {s+1} (kg)", min_value=0.0, value=0.0, step=0.5, key=f"form_set_w_{s}")
                        )
                    with col_r:
                        set_reps.append(
                            st.number_input(f"Set {s+1} (tekrar)", min_value=0, value=10, step=1, key=f"form_set_r_{s}")
                        )
            else:
                weight = st.number_input("Kaldırılan Ağırlık (kg)", min_value=0.1, value=50.0, step=0.5, key="form_weight")
                reps = st.number_input("Tekrar sayısı", min_value=1, value=10, step=1, key="form_reps")

            submitted = st.form_submit_button("Kaydet")

            if submitted:
                date_str = date_val.isoformat()
                to_save = []
                if detailed:
                    to_save = [
                        (float(w), max(1, int(r)))
                        for w, r in zip(set_weights, set_reps)
                        if w and float(w) > 0
                    ]
                else:
                    if weight and float(weight) > 0:
                        to_save = [(float(weight), max(1, int(reps)))]
                if not to_save:
                    st.error("En az bir set için ağırlık (0'dan büyük) girin.")
                else:
                    try:
                        ok_count = 0
                        for w, r in to_save:
                            row_id = add_progress_log(
                                date=date_str,
                                exercise_name=exercise_name,
                                weight_lifted=w,
                                reps=r,
                            )
                            if row_id is not None:
                                ok_count += 1
                        if ok_count:
                            st.cache_data.clear()
                            st.success(f"{ok_count} kayıt eklendi.")
                            st.rerun()
                        else:
                            st.error("Kayıt eklenirken veritabanı hatası oluştu.")
                    except Exception as e:
                        st.error(f"Kayıt eklenirken hata: {e}")

    st.markdown("---")

    with st.container():
        st.subheader("Hareket Gelişimi")
        selected = st.selectbox(
            "Grafik ve metrik için hareket seç",
            options=all_exercises,
            key="gelisim_secim",
        )

    try:
        aggregated = get_progress_logs_aggregated(selected)
    except Exception as e:
        st.error(f"Veri yüklenirken hata: {e}")
        aggregated = []

    if not aggregated:
        st.info("Bu hareket için henüz kayıt yok. Yukarıdan giriş yapabilirsin.")
    else:
        dates = [a["date"] for a in aggregated]
        max_weights = [a["max_weight"] for a in aggregated]

        with st.container():
            if len(max_weights) >= 2 and max_weights[-2] > 0:
                pct = ((max_weights[-1] - max_weights[-2]) / max_weights[-2]) * 100
                delta_str = f"%{pct:+.1f} Değişim (en yüksek ağırlık)"
            else:
                delta_str = None
            st.metric(label=selected, value=f"{max_weights[-1]} kg", delta=delta_str)
            st.caption("Değer: o tarihte kaldırdığın en yüksek ağırlık.")

        with st.container():
            try:
                fig = build_progress_line_chart(dates, max_weights, selected)
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Grafik oluşturulurken hata: {e}")

        # Tekrar dikkate alan özet: 1RM, volume, tablo
        with st.container():
            st.subheader("Tekrar dikkate alan özet (tahmini 1RM & volume)")
            st.caption("Tahmini 1RM: Epley formülü (ağırlık × (1 + tekrar/30)). Volume: toplam ağırlık×tekrar (kg).")
            rows = []
            for a in aggregated:
                weights_str = ", ".join(f"{w} kg" for w in a["weights"])
                reps_str = ", ".join(str(r) for r in a["reps_list"])
                rows.append({
                    "Tarih": a["date"],
                    "En yüksek (kg)": a["max_weight"],
                    "Setler (kg)": weights_str,
                    "Tekrarlar": reps_str,
                    "Tahmini 1RM (kg)": a["estimated_1rm"],
                    "Volume (kg)": a["volume"],
                })
            st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)

            try:
                est_1rms = [a["estimated_1rm"] for a in aggregated]
                fig_1rm = build_1rm_line_chart(dates, est_1rms, selected)
                st.plotly_chart(fig_1rm, use_container_width=True)
            except Exception as e:
                st.error(f"1RM grafiği hatası: {e}")

        with st.container():
            st.subheader("Set detayı (ağırlıklar)")
            rows_simple = []
            for a in aggregated:
                rows_simple.append({"Tarih": a["date"], "En yüksek (kg)": a["max_weight"], "Setler": ", ".join(f"{w} kg" for w in a["weights"])})
            st.dataframe(pd.DataFrame(rows_simple), hide_index=True, use_container_width=True)


if __name__ == "__main__":
    main()
