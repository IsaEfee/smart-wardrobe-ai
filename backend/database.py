import sqlite3
import os
import json
from datetime import datetime
from typing import List, Dict, Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "wardrobe_app.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        gender TEXT NOT NULL, -- 'Female' or 'Male'
        base_thermal_profile TEXT NOT NULL, -- 'Cold', 'Standard', 'Hot'
        personal_delta_clo REAL DEFAULT 0.0, -- Adaptive Learning Offset
        has_umbrella BOOLEAN DEFAULT 0,
        has_undershirt BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # 2. User Wardrobe table (stores owned items by their English unique ID/Name)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_wardrobe (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        category TEXT NOT NULL, -- 'top_inner', 'top_outer', 'bottom_inner', 'bottom_outer', 'accessories'
        item_en TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    )
    """)
    
    # 3. Feedback History table (tracks the online learning progression)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS feedback_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        feedback TEXT NOT NULL, -- 'cold', 'perfect', 'hot'
        temp_c REAL NOT NULL,
        base_clo REAL NOT NULL,
        applied_delta REAL NOT NULL,
        new_delta REAL NOT NULL,
        note TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    )
    """)
    
    conn.commit()
    conn.close()

# User CRUD
def create_or_update_user(user_id: Optional[int], name: str, gender: str, base_thermal: str, has_umbrella: bool, has_undershirt: bool) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    
    if user_id:
        cursor.execute("""
        UPDATE users 
        SET name = ?, gender = ?, base_thermal_profile = ?, has_umbrella = ?, has_undershirt = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """, (name, gender, base_thermal, int(has_umbrella), int(has_undershirt), user_id))
        uid = user_id
    else:
        cursor.execute("""
        INSERT INTO users (name, gender, base_thermal_profile, personal_delta_clo, has_umbrella, has_undershirt)
        VALUES (?, ?, ?, 0.0, ?, ?)
        """, (name, gender, base_thermal, int(has_umbrella), int(has_undershirt)))
        uid = cursor.lastrowid
        
    conn.commit()
    conn.close()
    return uid

def get_user(user_id: int) -> Optional[Dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def get_or_create_default_user(name: str = "İsa") -> Dict:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users ORDER BY id ASC LIMIT 1")
    row = cursor.fetchone()
    if row:
        user = dict(row)
        conn.close()
        return user
    
    # Create default user
    cursor.execute("""
    INSERT INTO users (name, gender, base_thermal_profile, personal_delta_clo, has_umbrella, has_undershirt)
    VALUES (?, 'Male', 'Standard', 0.0, 1, 1)
    """, (name,))
    uid = cursor.lastrowid
    conn.commit()
    cursor.execute("SELECT * FROM users WHERE id = ?", (uid,))
    user = dict(cursor.fetchone())
    conn.close()
    return user

# Wardrobe operations
def save_user_wardrobe(user_id: int, items_by_cat: Dict[str, List[str]]):
    """
    items_by_cat: {'top_inner': ['Shirt', 'Hoodie'], 'top_outer': [...], ...}
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM user_wardrobe WHERE user_id = ?", (user_id,))
    
    for category, items in items_by_cat.items():
        for item in items:
            cursor.execute("""
            INSERT INTO user_wardrobe (user_id, category, item_en)
            VALUES (?, ?, ?)
            """, (user_id, category, item))
            
    conn.commit()
    conn.close()

def get_user_wardrobe(user_id: int) -> Dict[str, List[str]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT category, item_en FROM user_wardrobe WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    
    wardrobe = {
        "top_inner": [],
        "top_outer": [],
        "bottom_inner": [],
        "bottom_outer": [],
        "accessories": []
    }
    for r in rows:
        cat = r["category"]
        if cat in wardrobe:
            wardrobe[cat].append(r["item_en"])
    return wardrobe

# Feedback & Online Learning
def record_user_feedback(user_id: int, feedback: str, temp_c: float, base_clo: float) -> Dict:
    """
    Human-in-the-Loop Dynamic Learning Step:
    - 'cold': delta += 0.05 (needs more warmth)
    - 'hot': delta -= 0.05 (needs less warmth)
    - 'perfect': delta unchanged (optimum convergence)
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT personal_delta_clo FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise ValueError(f"User {user_id} not found")
        
    current_delta = row["personal_delta_clo"]
    step = 0.05
    
    if feedback.lower() in ["cold", "üsüdüm", "üşüdüm"]:
        applied_delta = step
        new_delta = round(min(0.40, current_delta + step), 2)
        note = "Kullanıcı üşüdüğünü belirtti. Isı katsayısı +0.05 CLO artırıldı."
    elif feedback.lower() in ["hot", "sıcakladım", "terledim"]:
        applied_delta = -step
        new_delta = round(max(-0.40, current_delta - step), 2)
        note = "Kullanıcı sıcakladığını belirtti. Isı katsayısı -0.05 CLO düşürüldü."
    else: # perfect / ideal
        applied_delta = 0.0
        new_delta = current_delta
        note = "Kombin tam ideal bulundu. Isı profili optimum noktada."
        
    cursor.execute("""
    UPDATE users SET personal_delta_clo = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?
    """, (new_delta, user_id))
    
    cursor.execute("""
    INSERT INTO feedback_history (user_id, feedback, temp_c, base_clo, applied_delta, new_delta, note)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (user_id, feedback, temp_c, base_clo, applied_delta, new_delta, note))
    
    conn.commit()
    conn.close()
    
    return {
        "user_id": user_id,
        "previous_delta": current_delta,
        "new_delta": new_delta,
        "applied_step": applied_delta,
        "feedback": feedback,
        "note": note
    }

def get_user_feedback_history(user_id: int, limit: int = 10) -> List[Dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT * FROM feedback_history WHERE user_id = ? ORDER BY id DESC LIMIT ?
    """, (user_id, limit))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]
