"""GuardianAI - SQLite Database Manager"""

import sqlite3
import hashlib
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "guardian.db")


def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        phone TEXT NOT NULL UNIQUE,
        email TEXT,
        password_hash TEXT NOT NULL,
        address TEXT DEFAULT '',
        blood_group TEXT DEFAULT '',
        medical_notes TEXT DEFAULT '',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS emergency_contacts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        phone TEXT NOT NULL,
        relationship TEXT DEFAULT 'Contact',
        priority INTEGER DEFAULT 1,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS emergency_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        trigger_type TEXT NOT NULL,
        risk_score INTEGER DEFAULT 0,
        latitude REAL,
        longitude REAL,
        location_name TEXT DEFAULT '',
        status TEXT DEFAULT 'active',
        notes TEXT DEFAULT '',
        timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )""")

    conn.commit()
    conn.close()


def hash_pw(password):
    return hashlib.sha256(password.encode()).hexdigest()


# ── USER ─────────────────────────────────────────────────────────────────
def create_user(full_name, phone, email, password, address="", blood_group="", medical_notes=""):
    conn = get_conn()
    try:
        conn.execute(
            "INSERT INTO users (full_name, phone, email, password_hash, address, blood_group, medical_notes) VALUES (?,?,?,?,?,?,?)",
            (full_name, phone, email, hash_pw(password), address, blood_group, medical_notes)
        )
        conn.commit()
        return True, "Account created successfully!"
    except sqlite3.IntegrityError:
        return False, "Phone number already registered."
    finally:
        conn.close()


def login_user(phone, password):
    conn = get_conn()
    row = conn.execute(
        "SELECT * FROM users WHERE phone=? AND password_hash=?",
        (phone, hash_pw(password))
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def get_user(user_id):
    conn = get_conn()
    row = conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def update_user(user_id, **kwargs):
    conn = get_conn()
    fields = ", ".join(f"{k}=?" for k in kwargs)
    conn.execute(f"UPDATE users SET {fields} WHERE id=?", (*kwargs.values(), user_id))
    conn.commit()
    conn.close()


# ── CONTACTS ──────────────────────────────────────────────────────────────
def get_contacts(user_id):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM emergency_contacts WHERE user_id=? ORDER BY priority",
        (user_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_contact(user_id, name, phone, relationship, priority=1):
    conn = get_conn()
    conn.execute(
        "INSERT INTO emergency_contacts (user_id, name, phone, relationship, priority) VALUES (?,?,?,?,?)",
        (user_id, name, phone, relationship, priority)
    )
    conn.commit()
    conn.close()


def delete_contact(contact_id, user_id):
    conn = get_conn()
    conn.execute("DELETE FROM emergency_contacts WHERE id=? AND user_id=?", (contact_id, user_id))
    conn.commit()
    conn.close()


def update_contact(contact_id, user_id, name, phone, relationship, priority):
    conn = get_conn()
    conn.execute(
        "UPDATE emergency_contacts SET name=?, phone=?, relationship=?, priority=? WHERE id=? AND user_id=?",
        (name, phone, relationship, priority, contact_id, user_id)
    )
    conn.commit()
    conn.close()


# ── EMERGENCY LOG ─────────────────────────────────────────────────────────
def log_emergency(user_id, trigger_type, risk_score, lat=None, lon=None, location_name="", notes=""):
    conn = get_conn()
    conn.execute(
        "INSERT INTO emergency_log (user_id, trigger_type, risk_score, latitude, longitude, location_name, notes) VALUES (?,?,?,?,?,?,?)",
        (user_id, trigger_type, risk_score, lat, lon, location_name, notes)
    )
    conn.commit()
    conn.close()


def get_emergency_log(user_id, limit=20):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM emergency_log WHERE user_id=? ORDER BY timestamp DESC LIMIT ?",
        (user_id, limit)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def resolve_emergency(log_id, user_id):
    conn = get_conn()
    conn.execute(
        "UPDATE emergency_log SET status='resolved' WHERE id=? AND user_id=?",
        (log_id, user_id)
    )
    conn.commit()
    conn.close()
