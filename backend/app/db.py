"""Lichte SQLite-opslag voor mededeling, partners en agenda."""
import os
import sqlite3

DATA_DIR = os.environ.get("DATA_DIR", "/data")
DB_PATH = os.path.join(DATA_DIR, "radiowaver.db")

# Whitelist van tabellen + kolommen (kolomnamen komen nooit van de gebruiker).
TABLES = {
    "partners": ["name", "url", "logo", "sort"],
    "events": ["name", "label", "time", "description", "affiche", "sort"],
    "messages": ["text", "author", "status"],
}


def get_conn():
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)")
    c.execute(
        "CREATE TABLE IF NOT EXISTS partners ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, "
        "url TEXT, logo TEXT, sort INTEGER DEFAULT 0)"
    )
    c.execute(
        "CREATE TABLE IF NOT EXISTS events ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, label TEXT, "
        "time TEXT, description TEXT, affiche TEXT, sort INTEGER DEFAULT 0)"
    )
    # Migratie: kolommen toevoegen aan een bestaande events-tabel.
    for col in ("name TEXT", "description TEXT"):
        try:
            c.execute(f"ALTER TABLE events ADD COLUMN {col}")
        except sqlite3.OperationalError:
            pass
    c.execute(
        "CREATE TABLE IF NOT EXISTS messages ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, text TEXT NOT NULL, author TEXT, "
        "status TEXT DEFAULT 'pending', created TEXT DEFAULT CURRENT_TIMESTAMP)"
    )
    c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('announcement_enabled', '0')")
    c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('announcement_text', '')")
    c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('messages_enabled', '0')")
    conn.commit()
    conn.close()


# --- settings ---
def get_setting(key, default=None):
    conn = get_conn()
    row = conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    conn.close()
    return row["value"] if row else default


def set_setting(key, value):
    conn = get_conn()
    conn.execute(
        "INSERT INTO settings (key, value) VALUES (?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (key, value),
    )
    conn.commit()
    conn.close()


# --- generieke CRUD (tabel uit vaste whitelist) ---
def list_rows(table):
    conn = get_conn()
    rows = conn.execute(f"SELECT * FROM {table} ORDER BY sort, id").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_row(table, row_id):
    conn = get_conn()
    row = conn.execute(f"SELECT * FROM {table} WHERE id=?", (row_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def insert(table, data):
    cols = [k for k in TABLES[table] if k in data]
    conn = get_conn()
    cur = conn.execute(
        f"INSERT INTO {table} ({','.join(cols)}) VALUES ({','.join('?' * len(cols))})",
        [data[k] for k in cols],
    )
    conn.commit()
    rid = cur.lastrowid
    conn.close()
    return rid


def update(table, row_id, data):
    cols = [k for k in TABLES[table] if k in data]
    if not cols:
        return
    conn = get_conn()
    conn.execute(
        f"UPDATE {table} SET {','.join(c + '=?' for c in cols)} WHERE id=?",
        [data[k] for k in cols] + [row_id],
    )
    conn.commit()
    conn.close()


def delete(table, row_id):
    conn = get_conn()
    conn.execute(f"DELETE FROM {table} WHERE id=?", (row_id,))
    conn.commit()
    conn.close()


# --- berichten (live-ticker, gemodereerd) ---
def list_messages(status=None):
    conn = get_conn()
    if status:
        rows = conn.execute(
            "SELECT * FROM messages WHERE status=? ORDER BY id DESC", (status,)
        ).fetchall()
    else:
        # Pending bovenaan, daarna nieuwste eerst.
        rows = conn.execute(
            "SELECT * FROM messages ORDER BY (status='pending') DESC, id DESC"
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def set_message_status(row_id, status):
    conn = get_conn()
    conn.execute("UPDATE messages SET status=? WHERE id=?", (status, row_id))
    conn.commit()
    conn.close()
