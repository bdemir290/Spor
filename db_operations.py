"""
Veritabanı CRUD işlemleri: workouts, progress_logs, nutrition_logs.

Ekleme, okuma, güncelleme ve silme fonksiyonları bu modülde toplanmıştır.
"""

import sqlite3
from typing import Optional

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
    except sqlite3.Error:
        return None


def get_all_workouts():
    """
    Tüm antrenman programını liste olarak döndürür.

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
    except sqlite3.Error:
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
    except sqlite3.Error:
        return False


# ---------- Progress Logs (Ağırlık Geçmişi) ----------


def add_progress_log(date: str, exercise_name: str, weight_lifted: float) -> Optional[int]:
    """
    Ağırlık geçmişine yeni kayıt ekler.

    Args:
        date: Tarih (YYYY-MM-DD).
        exercise_name: Hareket adı.
        weight_lifted: Kaldırılan ağırlık (kg).

    Returns:
        Eklenen kaydın id'si veya hata durumunda None.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO progress_logs (date, exercise_name, weight_lifted)
            VALUES (?, ?, ?)
            """,
            (date, exercise_name, weight_lifted),
        )
        conn.commit()
        row_id = cursor.lastrowid
        conn.close()
        return row_id
    except sqlite3.Error:
        return None


def get_progress_logs(exercise_name: Optional[str] = None):
    """
    Ağırlık geçmişini döndürür. İsteğe bağlı olarak hareket adına göre filtreler.

    Args:
        exercise_name: Sadece bu hareketi getir. None ise tümü.

    Returns:
        List[dict]: date, exercise_name, weight_lifted (ve id) içeren kayıtlar.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        if exercise_name:
            cursor.execute(
                """
                SELECT id, date, exercise_name, weight_lifted
                FROM progress_logs WHERE exercise_name = ?
                ORDER BY date ASC
                """,
                (exercise_name,),
            )
        else:
            cursor.execute(
                """
                SELECT id, date, exercise_name, weight_lifted
                FROM progress_logs ORDER BY date ASC, exercise_name
                """
            )
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    except sqlite3.Error:
        return []


def get_distinct_exercises_from_progress():
    """
    progress_logs tablosunda geçen benzersiz hareket adlarını döndürür.

    Returns:
        List[str]: Hareket adları.
    """
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


# ---------- Nutrition Logs (Protein Takibi) ----------


def set_nutrition_for_date(date: str, protein_goal_met: bool) -> bool:
    """
    Belirtilen tarih için protein hedefi durumunu yazar veya günceller.

    Args:
        date: Tarih (YYYY-MM-DD).
        protein_goal_met: Hedef karşılandı mı (True/False).

    Returns:
        İşlem başarılı ise True, aksi halde False.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        value = 1 if protein_goal_met else 0
        cursor.execute(
            """
            INSERT INTO nutrition_logs (date, protein_goal_met)
            VALUES (?, ?)
            ON CONFLICT(date) DO UPDATE SET protein_goal_met = excluded.protein_goal_met
            """,
            (date, value),
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error:
        return False


def get_nutrition_for_date(date: str) -> Optional[bool]:
    """
    Belirtilen tarih için protein hedefi karşılandı mı bilgisini döndürür.

    Args:
        date: Tarih (YYYY-MM-DD).

    Returns:
        True/False veya kayıt yoksa None.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT protein_goal_met FROM nutrition_logs WHERE date = ?", (date,)
        )
        row = cursor.fetchone()
        conn.close()
        if row is None:
            return None
        return bool(row[0])
    except sqlite3.Error:
        return None


def get_nutrition_logs_all():
    """
    Tüm beslenme kayıtlarını tarih sırasıyla döndürür.

    Returns:
        List[dict]: date, protein_goal_met (1/0) içeren kayıtlar.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, date, protein_goal_met FROM nutrition_logs ORDER BY date ASC"
        )
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    except sqlite3.Error:
        return []


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
