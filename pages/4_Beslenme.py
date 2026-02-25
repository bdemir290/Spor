"""
Beslenme sayfası: Günlük protein hedefi işaretleme ve aylık takvim görünümü.

Bugünün tarihi otomatik alınır; checkbox ile hedef karşılandı işaretlenir.
Aylık takvimde hedefe ulaşılan günler yeşil, ulaşılmayanlar kırmızı/boş gösterilir.
"""

import calendar
import datetime

import streamlit as st
import pandas as pd

from auth import require_login
from components import inject_theme_css, render_sidebar
from db_operations import (
    set_nutrition_for_date,
    get_nutrition_for_date,
    get_nutrition_logs_all,
)


def get_month_calendar_data(year: int, month: int) -> dict[str, int]:
    """
    Verilen ay için her günün durumunu döndürür.
    1 = hedef karşılandı, 0 = karşılanmadı, -1 = kayıt yok.

    Returns:
        dict: "YYYY-MM-DD" -> 1/0/-1
    """
    try:
        logs = get_nutrition_logs_all()
        by_date = {}
        for row in logs:
            d = row["date"]
            if d.startswith(f"{year}-{month:02d}-"):
                by_date[d] = 1 if row["protein_goal_met"] else 0
        return by_date
    except Exception:
        return {}


def render_month_calendar(year: int, month: int) -> None:
    """Aylık takvimi HTML/CSS ile renkli kutucuklar (commit tarzı) olarak çizer."""
    cal = calendar.Calendar(calendar.MONDAY)
    month_days = cal.monthdays2calendar(year, month)
    data = get_month_calendar_data(year, month)

    day_names = ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"]
    html = "<div style='font-family: sans-serif;'>"
    html += f"<p><strong>{calendar.month_name[month]} {year}</strong></p>"
    html += "<table style='border-collapse: collapse; table-layout: fixed;'>"
    html += "<tr>"
    for d in day_names:
        html += f"<th style='padding:4px; font-size:11px;'>{d}</th>"
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
                    color = "#2ecc71"
                    title = "Hedef karşılandı"
                elif status == 0:
                    color = "#e74c3c"
                    title = "Hedef karşılanmadı"
                else:
                    color = "#ecf0f1"
                    title = "Kayıt yok"
                html += (
                    f"<td style='width:28px; height:28px; padding:2px;' "
                    f"title='{date_str} - {title}'>"
                    f"<div style='width:22px; height:22px; border-radius:4px; "
                    f"background:{color};'></div></td>"
                )
        html += "</tr>"
    html += "</table></div>"
    st.markdown(html, unsafe_allow_html=True)


def main():
    require_login()
    inject_theme_css()
    with st.sidebar:
        render_sidebar("Beslenme")
    st.title("🥗 Beslenme ve Takvim")
    st.markdown("Günlük protein hedefini işaretle ve aylık takvimde takip et.")

    today = datetime.date.today()
    today_str = today.isoformat()

    st.subheader(f"Bugün: {today_str}")
    try:
        current = get_nutrition_for_date(today_str)
    except Exception:
        current = None

    # Checkbox: Yeterince protein aldım
    new_value = st.checkbox(
        "Yeterince protein aldım (Örn: 120g)",
        value=current if current is not None else False,
        key="protein_checkbox",
    )

    if st.button("Kaydet"):
        try:
            ok = set_nutrition_for_date(today_str, new_value)
            if ok:
                st.success("Kaydedildi.")
                st.rerun()
            else:
                st.error("Kayıt sırasında hata oluştu.")
        except Exception:
            st.error("Kayıt sırasında hata oluştu.")

    st.markdown("---")
    st.subheader("Aylık Takvim")
    st.caption("Yeşil: hedef karşılandı, Kırmızı: karşılanmadı, Gri: kayıt yok")

    # Ay seçimi
    col1, col2 = st.columns(2)
    with col1:
        sel_year = st.selectbox(
            "Yıl",
            options=list(range(today.year, today.year - 2, -1)),
            index=0,
        )
    with col2:
        sel_month = st.selectbox(
            "Ay",
            options=list(range(1, 13)),
            index=today.month - 1,
            format_func=lambda m: calendar.month_name[m],
        )

    render_month_calendar(sel_year, sel_month)


if __name__ == "__main__":
    main()
