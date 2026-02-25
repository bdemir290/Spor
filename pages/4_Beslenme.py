"""
Beslenme: Günlük protein hedefi işaretleme, aylık takvim, Plotly ısı haritası.

Card layout; try-except ve st.error; kayıt sonrası cache temizlenir.
"""

import calendar
import datetime

import streamlit as st

from auth import require_login
from components import inject_theme_css, render_sidebar
from db_operations import (
    set_nutrition_for_date,
    get_nutrition_for_date,
    get_nutrition_logs_all,
)
from services.charts import build_nutrition_heatmap


def get_month_calendar_data(year: int, month: int) -> dict:
    """Verilen ay için günlük protein hedefi durumu: 1=tamam, 0=hayır, -1=kayıt yok."""
    try:
        logs = get_nutrition_logs_all()
        by_date = {}
        prefix = f"{year}-{month:02d}-"
        for row in logs:
            d = row["date"]
            if d.startswith(prefix):
                by_date[d] = 1 if row["protein_goal_met"] else 0
        return by_date
    except Exception:
        return {}


def render_month_calendar_html(year: int, month: int) -> None:
    """Aylık takvimi HTML kutucuklar (yeşil/kırmızı/gri) olarak çizer."""
    cal = calendar.Calendar(calendar.MONDAY)
    month_days = cal.monthdays2calendar(year, month)
    data = get_month_calendar_data(year, month)
    day_names = ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"]
    html = "<div style='font-family: sans-serif;'>"
    html += f"<p><strong>{calendar.month_name[month]} {year}</strong></p>"
    html += "<table style='border-collapse: collapse; table-layout: fixed;'>"
    html += "<tr>"
    for d in day_names:
        html += f"<th style='padding:4px; font-size:11px; color:#d1d5db;'>{d}</th>"
    html += "</tr>"
    for week in month_days:
        html += "<tr>"
        for day_num, _ in week:
            if day_num == 0:
                html += "<td style='width:28px; height:28px; padding:2px;'></td>"
            else:
                date_str = f"{year}-{month:02d}-{day_num:02d}"
                status = data.get(date_str, -1)
                if status == 1:
                    color, title = "#2ecc71", "Hedef karşılandı"
                elif status == 0:
                    color, title = "#e74c3c", "Hedef karşılanmadı"
                else:
                    color, title = "#ecf0f1", "Kayıt yok"
                html += (
                    f"<td style='width:28px; height:28px; padding:2px;' title='{date_str} – {title}'>"
                    f"<div style='width:22px; height:22px; border-radius:4px; background:{color};'></div></td>"
                )
        html += "</tr>"
    html += "</table></div>"
    st.markdown(html, unsafe_allow_html=True)


def main():
    require_login()
    inject_theme_css()
    with st.sidebar:
        render_sidebar("Beslenme")
        st.markdown("---")

    today = datetime.date.today()
    today_str = today.isoformat()

    with st.container():
        st.title("🥗 Beslenme ve Takvim")
        st.markdown("Günlük protein hedefini işaretle ve aylık takvimde takip et.")

    with st.container():
        st.subheader(f"Bugün: {today_str}")
        try:
            current = get_nutrition_for_date(today_str)
        except Exception as e:
            st.error(f"Bugünkü kayıt yüklenirken hata: {e}")
            current = None

        new_value = st.checkbox(
            "Yeterince protein aldım (Örn: 120g)",
            value=current if current is not None else False,
            key="protein_checkbox",
        )

        if st.button("Kaydet"):
            try:
                ok = set_nutrition_for_date(today_str, new_value)
                if ok:
                    st.cache_data.clear()
                    st.success("Kaydedildi.")
                    st.rerun()
                else:
                    st.error("Kayıt sırasında veritabanı hatası oluştu.")
            except Exception as e:
                st.error(f"Kayıt sırasında hata: {e}")

    st.markdown("---")

    with st.container():
        st.subheader("Aylık Takvim")
        st.caption("Yeşil: hedef karşılandı | Kırmızı: karşılanmadı | Gri: kayıt yok")

        col1, col2 = st.columns(2)
        with col1:
            sel_year = st.selectbox(
                "Yıl",
                options=list(range(today.year, today.year - 2, -1)),
                index=0,
                key="cal_year",
            )
        with col2:
            sel_month = st.selectbox(
                "Ay",
                options=list(range(1, 13)),
                index=today.month - 1,
                format_func=lambda m: calendar.month_name[m],
                key="cal_month",
            )

        try:
            date_status = get_month_calendar_data(sel_year, sel_month)
        except Exception as e:
            st.error(f"Takvim verisi yüklenirken hata: {e}")
            date_status = {}

        # Plotly ısı haritası (opsiyonel) + HTML takvim
        try:
            fig = build_nutrition_heatmap(sel_year, sel_month, date_status)
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Isı haritası oluşturulurken hata: {e}")

        render_month_calendar_html(sel_year, sel_month)


if __name__ == "__main__":
    main()
