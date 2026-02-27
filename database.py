"""
Veritabanı modülü: SQLite tablo oluşturma ve bağlantı yönetimi.

Bu modül spor_uygulamasi veritabanı için gerekli tabloları oluşturur
ve bağlantı fonksiyonları sağlar.
"""

import os
import sqlite3
from pathlib import Path


def get_db_path():
    """
    Veritabanı dosyasının tam yolunu döndürür.
    Önce SPOR_DB_PATH ortam değişkenine bakar; yoksa uygulama klasöründe 'spor.db' kullanır.
    (Streamlit Cloud gibi salt-okunur ortamlarda SPOR_DB_PATH ile yazılabilir bir yol verin.)

    Returns:
        str: Veritabanı dosya yolu.
    """
    env_path = os.environ.get("SPOR_DB_PATH")
    if env_path:
        return os.path.abspath(env_path)
    base_dir = Path(__file__).resolve().parent
    path = base_dir / "spor.db"
    return str(path)


def get_connection():
    """
    SQLite veritabanına bağlantı açar.

    Returns:
        sqlite3.Connection: Veritabanı bağlantı nesnesi.

    Raises:
        sqlite3.Error: Bağlantı hatası durumunda.
    """
    try:
        conn = sqlite3.connect(get_db_path())
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        raise sqlite3.Error(f"Veritabanı bağlantı hatası: {e}") from e


def create_tables(conn=None):
    """
    Tüm gerekli tabloları oluşturur. Tablo yoksa oluşturulur.

    Tablolar:
        - workouts: Gün, hareket adı, set, tekrar (antrenman programı).
        - progress_logs: Tarih, hareket adı, kaldırılan ağırlık.
        - nutrition_logs: Tarih, protein hedefi karşılandı mı (1/0).

    Args:
        conn: Mevcut bağlantı. None ise yeni bağlantı açılır.

    Returns:
        None
    """
    close_after = conn is None
    try:
        if conn is None:
            conn = get_connection()

        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS workouts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                day_name TEXT NOT NULL,
                exercise_name TEXT NOT NULL,
                sets INTEGER NOT NULL,
                reps INTEGER NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS progress_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                exercise_name TEXT NOT NULL,
                weight_lifted REAL NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS nutrition_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL UNIQUE,
                protein_goal_met INTEGER NOT NULL
            )
        """)

        try:
            cursor.execute(
                "ALTER TABLE nutrition_logs ADD COLUMN vitamin_taken INTEGER NOT NULL DEFAULT 0"
            )
        except sqlite3.OperationalError:
            pass

        try:
            cursor.execute(
                "ALTER TABLE progress_logs ADD COLUMN reps INTEGER NOT NULL DEFAULT 1"
            )
        except sqlite3.OperationalError:
            pass

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS body_weight_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL UNIQUE,
                weight_kg REAL NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)

        conn.commit()
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        raise sqlite3.Error(f"Tablo oluşturma hatası: {e}") from e
    finally:
        if close_after and conn:
            conn.close()
