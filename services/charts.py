"""
Plotly grafik oluşturma: haftalık özet, gelişim çizgisi, beslenme ısı haritası.

Tema renkleri config ile uyumlu (koyu arka plan, neon yeşil vurgu).
"""

from typing import List

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# Tema: koyu arka plan, yeşil vurgu
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(26,29,36,0.9)",
    plot_bgcolor="rgba(26,29,36,0.9)",
    font=dict(color="#d1d5db", size=12),
    margin=dict(l=40, r=40, t=40, b=40),
    xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.08)"),
    yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.08)"),
    hovermode="x unified",
)


def build_weekly_weight_chart(weekly_totals: List[dict]) -> go.Figure:
    """
    Haftalık toplam kaldırılan ağırlık için bar grafik.

    Args:
        weekly_totals: [{"week_start": "YYYY-MM-DD", "total_kg": float}, ...]

    Returns:
        plotly.graph_objects.Figure
    """
    if not weekly_totals:
        fig = go.Figure()
        fig.add_annotation(text="Henüz veri yok", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        fig.update_layout(**PLOTLY_LAYOUT)
        return fig
    df = pd.DataFrame(weekly_totals)
    df["week_label"] = pd.to_datetime(df["week_start"]).dt.strftime("%d %b")
    fig = go.Figure(
        data=[go.Bar(x=df["week_label"], y=df["total_kg"], marker_color="#00e676", name="Toplam (kg)")]
    )
    fig.update_layout(
        **PLOTLY_LAYOUT,
        title=dict(text="Haftalık Toplam Kaldırılan Ağırlık", font=dict(size=14)),
        xaxis_title="Hafta",
        yaxis_title="kg",
        showlegend=False,
    )
    return fig


def build_progress_line_chart(
    dates: List[str], weights: List[float], exercise_name: str
) -> go.Figure:
    """
    Hareket gelişimi için çizgi grafik (tarih x ağırlık).

    Args:
        dates: Tarih listesi (YYYY-MM-DD).
        weights: Ağırlık listesi (kg).
        exercise_name: Hareket adı (başlık için).
    """
    if not dates or not weights:
        fig = go.Figure()
        fig.add_annotation(text="Bu hareket için veri yok", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        fig.update_layout(**PLOTLY_LAYOUT)
        return fig
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=weights,
            mode="lines+markers",
            line=dict(color="#00e676", width=2),
            marker=dict(size=8),
            name="Ağırlık (kg)",
        )
    )
    fig.update_layout(
        **PLOTLY_LAYOUT,
        title=dict(text=f"{exercise_name} – Gelişim", font=dict(size=14)),
        xaxis_title="Tarih",
        yaxis_title="kg",
        showlegend=False,
    )
    fig.update_xaxes(tickformat="%d.%m.%Y")
    return fig


def build_nutrition_heatmap(
    year: int, month: int, date_status: dict
) -> go.Figure:
    """
    Aylık protein hedefi ısı haritası (takvim grid).
    date_status: "YYYY-MM-DD" -> 1 (hedef tamam), 0 (tamamlanmadı), -1 (kayıt yok).

    Returns:
        plotly.graph_objects.Figure
    """
    import calendar
    cal = calendar.Calendar(calendar.MONDAY)
    month_days = cal.monthdays2calendar(year, month)
    rows = []
    day_names = ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"]
    for week in month_days:
        row = []
        for day_num, _ in week:
            if day_num == 0:
                row.append(None)
            else:
                date_str = f"{year}-{month:02d}-{day_num:02d}"
                row.append(date_status.get(date_str, -1))
        rows.append(row)
    z = rows
    z_mapped = []
    for row in z:
        z_mapped.append([
            0 if v is None else (0.33 if v == -1 else (0.66 if v == 0 else 1.0))
            for v in row
        ])
    fig = go.Figure(
        data=go.Heatmap(
            z=z_mapped,
            x=day_names,
            y=[f"Hafta {i+1}" for i in range(len(z))],
            colorscale=[[0, "#1a1d24"], [0.33, "#ecf0f1"], [0.66, "#e74c3c"], [1, "#2ecc71"]],
            showscale=True,
            colorbar=dict(title="Hedef", tickvals=[0.165, 0.5, 0.83], ticktext=["Kayıt yok", "Hayır", "Evet"]),
        )
    )
    fig.update_layout(
        **PLOTLY_LAYOUT,
        title=dict(text=f"{calendar.month_name[month]} {year} – Protein Hedefi", font=dict(size=14)),
        height=200,
    )
    return fig
