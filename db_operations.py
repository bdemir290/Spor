"""
Veritabanı CRUD işlemleri: workouts, progress_logs, nutrition_logs.

Okuma fonksiyonları @st.cache_data ile önbelleklenir; yazma sonrası
sayfa tarafında st.cache_data.clear() çağrılmalıdır.
"""

import sqlite3
from typing import Optional

import streamlit as st

from database import get_connection, create_tables


# ---------- Workouts (Antrenman Programı) ----------


def add_workout(day_name: str, exercise_name: str, sets: int, reps: int) -> Optional[int]:
    """
    Antrenman programına yeni bir hareket ekler.

    Args:
        day_name: Gün adı (örn. Pazartesi).
        exercise_name: Hareket adı.
        sets: Set sayısı.
        reps: Tekrar sayısı.

    Returns:
        Eklenen kaydın id'si veya hata durumunda None.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO workouts (day_name, exercise_name, sets, reps)
            VALUES (?, ?, ?, ?)
            """,
            (day_name, exercise_name, sets, reps),
        )
        conn.commit()
        row_id = cursor.lastrowid
        conn.close()
        return row_id
    except sqlite3.Error as e:
        raise RuntimeError(f"Veritabanına yazılamadı: {e}") from e


@st.cache_data(ttl=300)
def get_all_workouts():
    """
    Tüm antrenman programını liste olarak döndürür (önbellekli).

    Returns:
        List[dict]: Her eleman id, day_name, exercise_name, sets, reps içerir.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, day_name, exercise_name, sets, reps FROM workouts ORDER BY day_name, id"
        )
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    except sqlite3.Error as e:
        return []


def delete_workout(workout_id: int) -> bool:
    """
    Belirtilen id'ye sahip antrenman kaydını siler.

    Args:
        workout_id: Silinecek kaydın id'si.

    Returns:
        Silme başarılı ise True, aksi halde False.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM workouts WHERE id = ?", (workout_id,))
        conn.commit()
        deleted = cursor.rowcount > 0
        conn.close()
        return deleted
    except sqlite3.Error as e:
        raise RuntimeError(f"Kayıt silinemedi: {e}") from e


# ---------- Progress Logs (Ağırlık Geçmişi) ----------


def add_progress_log(
    date: str, exercise_name: str, weight_lifted: float, reps: int = 1
) -> Optional[int]:
    """
    Ağırlık geçmişine yeni kayıt ekler (ağırlık + tekrar).

    Args:
        date: Tarih (YYYY-MM-DD).
        exercise_name: Hareket adı.
        weight_lifted: Kaldırılan ağırlık (kg).
        reps: O sette yapılan tekrar sayısı (tahmini 1RM ve volume için).

    Returns:
        Eklenen kaydın id'si veya hata durumunda None.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        reps = max(1, int(reps))
        cursor.execute(
            """
            INSERT INTO progress_logs (date, exercise_name, weight_lifted, reps)
            VALUES (?, ?, ?, ?)
            """,
            (date, exercise_name, weight_lifted, reps),
        )
        conn.commit()
        row_id = cursor.lastrowid
        conn.close()
        return row_id
    except sqlite3.Error as e:
        raise RuntimeError(f"Antrenman kaydı yazılamadı: {e}") from e


@st.cache_data(ttl=300)
def get_progress_logs(exercise_name: Optional[str] = None):
    """
    Ağırlık geçmişini döndürür (önbellekli). İsteğe bağlı hareket filtresi.

    Returns:
        List[dict]: date, exercise_name, weight_lifted (ve id) içeren kayıtlar.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        if exercise_name:
            cursor.execute(
                """
                SELECT id, date, exercise_name, weight_lifted, reps
                FROM progress_logs WHERE exercise_name = ?
                ORDER BY date ASC
                """,
                (exercise_name,),
            )
        else:
            cursor.execute(
                """
                SELECT id, date, exercise_name, weight_lifted, reps
                FROM progress_logs ORDER BY date ASC, exercise_name
                """
            )
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    except sqlite3.Error:
        return []


@st.cache_data(ttl=300)
def get_distinct_exercises_from_progress():
    """progress_logs tablosundaki benzersiz hareket adlarını döndürür (önbellekli)."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT DISTINCT exercise_name FROM progress_logs ORDER BY exercise_name"
        )
        rows = cursor.fetchall()
        conn.close()
        return [row[0] for row in rows]
    except sqlite3.Error:
        return []


def _epley_1rm(weight: float, reps: int) -> float:
    """Epley formülü: tahmini tek tekrar maksimum (1RM). reps=1 ise 1RM=weight."""
    if reps <= 0:
        return weight
    if reps == 1:
        return weight
    return weight * (1 + reps / 30.0)


@st.cache_data(ttl=300)
def get_progress_logs_aggregated(exercise_name: str):
    """
    Hareket için tarih bazlı özet: max ağırlık, setler, tahmini 1RM, volume (ağırlık×tekrar toplamı).
    Her satırda reps varsa kullanılır; yoksa 1 kabul edilir.

    Returns:
        List[dict]: date, max_weight, weights, reps_list, estimated_1rm, volume
    """
    try:
        rows = get_progress_logs(exercise_name)
        from collections import defaultdict
        by_date = defaultdict(list)
        for r in rows:
            w = r["weight_lifted"]
            rep = int(r["reps"]) if "reps" in r.keys() and r["reps"] is not None else 1
            by_date[r["date"]].append((w, rep))
        result = []
        for date in sorted(by_date.keys()):
            pairs = by_date[date]
            weights = [p[0] for p in pairs]
            reps_list = [p[1] for p in pairs]
            max_weight = max(weights)
            estimated_1rm = max(_epley_1rm(w, r) for w, r in pairs)
            volume = sum(w * r for w, r in pairs)
            result.append({
                "date": date,
                "max_weight": max_weight,
                "weights": weights,
                "reps_list": reps_list,
                "estimated_1rm": round(estimated_1rm, 1),
                "volume": round(volume, 1),
            })
        return result
    except Exception:
        return []


# ---------- Nutrition Logs (Protein Takibi) ----------


def set_nutrition_for_date(
    date: str, protein_goal_met: bool, vitamin_taken: bool = False
) -> bool:
    """
    Belirtilen tarih için protein ve vitamin durumunu yazar veya günceller.

    Args:
        date: Tarih (YYYY-MM-DD).
        protein_goal_met: Protein hedefi karşılandı mı.
        vitamin_taken: Vitamin alındı mı.

    Returns:
        İşlem başarılı ise True, aksi halde False.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        pv = 1 if protein_goal_met else 0
        vv = 1 if vitamin_taken else 0
        cursor.execute(
            """
            INSERT INTO nutrition_logs (date, protein_goal_met, vitamin_taken)
            VALUES (?, ?, ?)
            ON CONFLICT(date) DO UPDATE SET
                protein_goal_met = excluded.protein_goal_met,
                vitamin_taken = excluded.vitamin_taken
            """,
            (date, pv, vv),
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        raise RuntimeError(f"Beslenme kaydı yazılamadı: {e}") from e


@st.cache_data(ttl=300)
def get_nutrition_for_date(date: str) -> Optional[dict]:
    """
    Belirtilen tarih için protein ve vitamin durumunu döndürür (önbellekli).

    Returns:
        {"protein_goal_met": bool, "vitamin_taken": bool} veya kayıt yoksa None.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT protein_goal_met, vitamin_taken FROM nutrition_logs WHERE date = ?",
            (date,),
        )
        row = cursor.fetchone()
        conn.close()
        if row is None:
            return None
        return {
            "protein_goal_met": bool(row[0]),
            "vitamin_taken": bool(row[1]) if len(row) > 1 else False,
        }
    except sqlite3.Error:
        return None


@st.cache_data(ttl=300)
def get_nutrition_logs_all():
    """Tüm beslenme kayıtlarını tarih sırasıyla döndürür (önbellekli)."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, date, protein_goal_met, vitamin_taken FROM nutrition_logs ORDER BY date ASC"
        )
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    except sqlite3.Error:
        return []


@st.cache_data(ttl=300)
def get_current_streak() -> int:
    """
    Bugünden geriye doğru kesintisiz protein hedefi karşılanan gün sayısını (seri) hesaplar.
    Bugün karşılanmadıysa 0 döner.

    Returns:
        int: Mevcut seri (gün sayısı).
    """
    try:
        import datetime
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT date, protein_goal_met FROM nutrition_logs WHERE protein_goal_met = 1"
        )
        rows = cursor.fetchall()
        conn.close()

        met_dates = {row["date"] for row in rows}
        today = datetime.date.today().isoformat()
        if today not in met_dates:
            return 0

        streak = 0
        current = today
        while current in met_dates:
            streak += 1
            d = datetime.datetime.strptime(current, "%Y-%m-%d").date()
            current = (d - datetime.timedelta(days=1)).isoformat()

        return streak
    except (sqlite3.Error, ValueError):
        return 0


# ---------- Dashboard istatistikleri ----------


@st.cache_data(ttl=300)
def get_total_weight_lifted_this_week() -> float:
    """
    Bu hafta kaldırılan toplam ağırlığı (set bazında değil, kayıt bazında) döndürür.
    Her progress kaydı bir antrenman gününde o hareket için kaldırılan ağırlık;
    toplam = sum(weight_lifted) bu hafta.

    Returns:
        float: Toplam kg.
    """
    try:
        import datetime
        conn = get_connection()
        cursor = conn.cursor()
        today = datetime.date.today()
        start_week = today - datetime.timedelta(days=today.weekday())
        start_str = start_week.isoformat()
        end_str = today.isoformat()
        cursor.execute(
            """
            SELECT COALESCE(SUM(weight_lifted), 0) AS total
            FROM progress_logs WHERE date >= ? AND date <= ?
            """,
            (start_str, end_str),
        )
        row = cursor.fetchone()
        conn.close()
        return float(row[0]) if row else 0.0
    except (sqlite3.Error, ValueError):
        return 0.0


@st.cache_data(ttl=300)
def get_workout_count_this_week() -> int:
    """
    Bu hafta kaç antrenman (benzersiz tarih) kaydı olduğunu döndürür.

    Returns:
        int: Antrenman günü sayısı.
    """
    try:
        import datetime
        conn = get_connection()
        cursor = conn.cursor()
        today = datetime.date.today()
        start_week = today - datetime.timedelta(days=today.weekday())
        start_str = start_week.isoformat()
        end_str = today.isoformat()
        cursor.execute(
            """
            SELECT COUNT(DISTINCT date) AS cnt FROM progress_logs
            WHERE date >= ? AND date <= ?
            """,
            (start_str, end_str),
        )
        row = cursor.fetchone()
        conn.close()
        return int(row[0]) if row else 0
    except (sqlite3.Error, ValueError):
        return 0


@st.cache_data(ttl=300)
def get_weekly_totals(weeks: int = 4):
    """
    Son N hafta için haftalık toplam kaldırılan ağırlığı döndürür (grafik için).

    Returns:
        List[dict]: week_start (Pazartesi), total_kg
    """
    try:
        import datetime
        conn = get_connection()
        cursor = conn.cursor()
        today = datetime.date.today()
        start_this_week = today - datetime.timedelta(days=today.weekday())
        result = []
        for i in range(weeks):
            start_week = start_this_week - datetime.timedelta(days=7 * (weeks - i))
            end_week = start_week + datetime.timedelta(days=6)
            start_str = start_week.isoformat()
            end_str = end_week.isoformat()
            cursor.execute(
                """
                SELECT COALESCE(SUM(weight_lifted), 0) AS total
                FROM progress_logs WHERE date >= ? AND date <= ?
                """,
                (start_str, end_str),
            )
            row = cursor.fetchone()
            total = float(row[0]) if row else 0.0
            result.append({"week_start": start_str, "total_kg": total})
        conn.close()
        return result
    except (sqlite3.Error, ValueError):
        return []


# ---------- Kişisel rekor (PR) ve son antrenman ----------


@st.cache_data(ttl=300)
def get_pr(exercise_name: str) -> Optional[float]:
    """Hareket için şu ana kadarki en yüksek kaldırılan ağırlığı (kg) döndürür."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT MAX(weight_lifted) FROM progress_logs WHERE exercise_name = ?",
            (exercise_name,),
        )
        row = cursor.fetchone()
        conn.close()
        return float(row[0]) if row and row[0] is not None else None
    except (sqlite3.Error, ValueError):
        return None


@st.cache_data(ttl=300)
def get_all_prs():
    """Tüm hareketler için kişisel rekorları döndürür: [{exercise_name, pr_kg}, ...]."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT exercise_name, MAX(weight_lifted) AS pr_kg
            FROM progress_logs GROUP BY exercise_name ORDER BY pr_kg DESC
            """
        )
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    except sqlite3.Error:
        return []


@st.cache_data(ttl=300)
def get_last_workout_date() -> Optional[str]:
    """Son antrenman tarihini (YYYY-MM-DD) döndürür; kayıt yoksa None."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT MAX(date) FROM progress_logs"
        )
        row = cursor.fetchone()
        conn.close()
        return row[0] if row and row[0] else None
    except sqlite3.Error:
        return None


# ---------- Vücut ağırlığı ----------


def add_body_weight(date: str, weight_kg: float) -> bool:
    """Belirtilen tarih için vücut ağırlığı kaydı ekler veya günceller."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO body_weight_log (date, weight_kg) VALUES (?, ?)
            ON CONFLICT(date) DO UPDATE SET weight_kg = excluded.weight_kg
            """,
            (date, weight_kg),
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        raise RuntimeError(f"Vücut ağırlığı kaydı yazılamadı: {e}") from e


@st.cache_data(ttl=300)
def get_body_weight_logs(limit: int = 90):
    """Son N günün vücut ağırlığı kayıtlarını döndürür (tarih sıralı)."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT date, weight_kg FROM body_weight_log ORDER BY date DESC LIMIT ?",
            (limit,),
        )
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    except sqlite3.Error:
        return []


# ---------- Haftalık hedef (user_settings) ----------


def get_weekly_goal() -> int:
    """Haftalık antrenman hedefi (sayı); yoksa 4 döner."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM user_settings WHERE key = ?", ("weekly_workout_goal",))
        row = cursor.fetchone()
        conn.close()
        return int(row["value"]) if row else 4
    except (sqlite3.Error, ValueError):
        return 4


def set_weekly_goal(goal: int) -> bool:
    """Haftalık antrenman hedefini kaydeder."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO user_settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            ("weekly_workout_goal", str(max(1, min(7, goal)))),
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        raise RuntimeError(f"Haftalık hedef kaydedilemedi: {e}") from e
