from enum import Enum
import sqlite3

from datetime import datetime, timedelta, timezone


DB_NAME = "search_history.db"


class CacheStatus(Enum):
    HIT = "HIT"
    MISS = "MISS"
    STALE = "STALE"


def get_conn():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_conn() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS SearchHistory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        ) """)

        conn.execute("""CREATE TABLE IF NOT EXISTS CachedStockData (
          ticker TEXT PRIMARY KEY,
          company_json TEXT,
          stock_json TEXT,
          last_updated DATETIME
        ) """)


def get_cache_results(ticker):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM CachedStockData WHERE ticker = ?", (ticker.upper(),)
        ).fetchone()

        # cache MISS (ticker not in cache)
        if row is None:
            return CacheStatus.MISS, None

        last_updated = datetime.fromisoformat(row["last_updated"])
        if datetime.now(timezone.utc) - last_updated < timedelta(minutes=15):
            # cache HIT
            return CacheStatus.HIT, row

        # STALE data (data out of date)
        return CacheStatus.STALE, None


def update_cache(ticker, company_json, stock_json):
    with get_conn() as conn:
        conn.execute(
            """
            UPDATE CachedStockData
            SET company_json = ?, stock_json = ?, last_updated = ?
            WHERE ticker = ?
            """,
            (
                company_json,
                stock_json,
                datetime.now(timezone.utc),
                ticker.upper(),
            ),
        )


def insert_cache(ticker, company_json, stock_json):
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO CachedStockData (ticker, company_json, stock_json, last_updated)
            VALUES (?, ?, ?, ?)
            """,
            (
                ticker.upper(),
                company_json,
                stock_json,
                datetime.now(timezone.utc),
            ),
        )


def add_search(ticker):
    with get_conn() as conn:
        conn.execute("INSERT INTO SearchHistory (ticker) VALUES (?)", (ticker.upper(),))


def get_recent_searches(limit=10):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT ticker, timestamp FROM SearchHistory ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()

        list_rows = []
        for row in rows:
            list_rows.append(dict(row))

        return list_rows
