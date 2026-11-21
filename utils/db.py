import sqlite3
import json
import datetime
import os

DB_DIR = os.environ.get("DB_DIR")
if not DB_DIR and os.environ.get("VERCEL"):
    DB_DIR = "/tmp"

if DB_DIR:
    DB_PATH = os.path.join(DB_DIR, "snapdiet.db")
    bundled_db = os.path.join(os.path.dirname(os.path.dirname(__file__)), "snapdiet.db")
    if not os.path.exists(DB_PATH) and os.path.exists(bundled_db):
        import shutil
        try:
            shutil.copyfile(bundled_db, DB_PATH)
        except Exception:
            pass
else:
    DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "snapdiet.db")

def get_connection():
    need_init = not os.path.exists(DB_PATH)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    if need_init:
        try:
            init_db()
        except Exception:
            pass
    return conn

def init_db():
    conn = get_connection()
    c = conn.cursor()
    
    # 1. User Profile Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            age INTEGER,
            sex TEXT,
            height REAL,
            weight REAL,
            target_weight REAL,
            activity_level TEXT,
            diet_pref TEXT,
            budget REAL,
            target_calories REAL,
            tdee REAL,
            macros JSON,
            diet_plan JSON,
            workout_type TEXT,
            mobile TEXT
        )
    ''')
    
    # Migration: Add diet_plan column if it doesn't exist
    try:
        c.execute("ALTER TABLE users ADD COLUMN diet_plan JSON")
    except sqlite3.OperationalError:
        pass # Column already exists
        
    # Migration: Add workout_type column if it doesn't exist
    try:
        c.execute("ALTER TABLE users ADD COLUMN workout_type TEXT")
    except sqlite3.OperationalError:
        pass # Column already exists

    # Migration: Add mobile column if it doesn't exist
    try:
        c.execute("ALTER TABLE users ADD COLUMN mobile TEXT")
    except sqlite3.OperationalError:
        pass # Column already exists

    # Migration: Add email column if it doesn't exist
    try:
        c.execute("ALTER TABLE users ADD COLUMN email TEXT")
    except sqlite3.OperationalError:
        pass

    # Migration: Add google_id column if it doesn't exist
    try:
        c.execute("ALTER TABLE users ADD COLUMN google_id TEXT")
    except sqlite3.OperationalError:
        pass

    # Migration: Add auth_provider column if it doesn't exist
    try:
        c.execute("ALTER TABLE users ADD COLUMN auth_provider TEXT")
    except sqlite3.OperationalError:
        pass

    # Migration: Add is_profile_completed column if it doesn't exist
    try:
        c.execute("ALTER TABLE users ADD COLUMN is_profile_completed INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass

    # Migration: Add avatar_url column if it doesn't exist
    try:
        c.execute("ALTER TABLE users ADD COLUMN avatar_url TEXT")
    except sqlite3.OperationalError:
        pass
    
    # 2. Daily Logs Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS daily_logs (
            date TEXT PRIMARY KEY,
            calories REAL DEFAULT 0,
            protein REAL DEFAULT 0,
            carbs REAL DEFAULT 0,
            fats REAL DEFAULT 0,
            water REAL DEFAULT 0
        )
    ''')
    
    # 3. Family Members Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS family_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            relation TEXT,
            age INTEGER,
            sex TEXT,
            weight REAL,
            activity TEXT,
            stats JSON
        )
    ''')
    
    # 4. Chat History Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT,
            content TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

# --- User Profile Methods ---
def _format_user_row(row):
    if not row:
        return None
    profile = dict(row)
    profile['macros'] = json.loads(profile['macros']) if profile.get('macros') else {}
    profile['diet_plan'] = json.loads(profile['diet_plan']) if profile.get('diet_plan') else None
    profile['is_profile_completed'] = bool(profile.get('is_profile_completed', 0))
    return profile

def get_user_profile():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users ORDER BY id DESC LIMIT 1")
    row = c.fetchone()
    conn.close()
    return _format_user_row(row)

def get_user_by_id(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return _format_user_row(row)

def get_user_by_email(email):
    if not email:
        return None
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email = ? ORDER BY id DESC LIMIT 1", (email,))
    row = c.fetchone()
    conn.close()
    return _format_user_row(row)

def get_user_by_google_id(google_id):
    if not google_id:
        return None
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE google_id = ? ORDER BY id DESC LIMIT 1", (google_id,))
    row = c.fetchone()
    conn.close()
    return _format_user_row(row)

def get_user_profile_by_mobile(mobile):
    if not mobile:
        return None
    # strip whitespace and non-digits for comparison if needed
    cleaned_mobile = mobile.strip()
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE mobile = ? OR mobile = ? ORDER BY id DESC LIMIT 1", (cleaned_mobile, cleaned_mobile[-10:] if len(cleaned_mobile) >= 10 else cleaned_mobile))
    row = c.fetchone()
    conn.close()
    return _format_user_row(row)

def save_user_profile(profile):
    conn = get_connection()
    c = conn.cursor()
    
    user_id = profile.get('id')
    is_completed = 1 if (profile.get('height') and profile.get('weight') and profile.get('age')) else profile.get('is_profile_completed', 0)
    
    if user_id:
        c.execute('''
            UPDATE users SET
                name = COALESCE(?, name),
                age = COALESCE(?, age),
                sex = COALESCE(?, sex),
                height = COALESCE(?, height),
                weight = COALESCE(?, weight),
                target_weight = COALESCE(?, target_weight),
                activity_level = COALESCE(?, activity_level),
                diet_pref = COALESCE(?, diet_pref),
                budget = COALESCE(?, budget),
                target_calories = COALESCE(?, target_calories),
                tdee = COALESCE(?, tdee),
                macros = COALESCE(?, macros),
                diet_plan = COALESCE(?, diet_plan),
                workout_type = COALESCE(?, workout_type),
                mobile = COALESCE(?, mobile),
                email = COALESCE(?, email),
                google_id = COALESCE(?, google_id),
                auth_provider = COALESCE(?, auth_provider),
                avatar_url = COALESCE(?, avatar_url),
                is_profile_completed = ?
            WHERE id = ?
        ''', (
            profile.get('name'), profile.get('age'), profile.get('sex'), profile.get('height'),
            profile.get('weight'), profile.get('target_weight'), profile.get('activity_level'),
            profile.get('diet_pref'), profile.get('budget'), profile.get('target_calories'),
            profile.get('tdee'), json.dumps(profile.get('macros', {})) if profile.get('macros') is not None else None,
            json.dumps(profile.get('diet_plan')) if profile.get('diet_plan') is not None else None,
            profile.get('workout_type'), profile.get('mobile'), profile.get('email'),
            profile.get('google_id'), profile.get('auth_provider'), profile.get('avatar_url'),
            1 if is_completed else 0, user_id
        ))
    else:
        # Check if user already exists by mobile, email or google_id
        existing = None
        if profile.get('google_id'):
            existing = get_user_by_google_id(profile.get('google_id'))
        elif profile.get('email'):
            existing = get_user_by_email(profile.get('email'))
        elif profile.get('mobile'):
            existing = get_user_profile_by_mobile(profile.get('mobile'))
            
        if existing:
            return save_user_profile({**existing, **profile, 'id': existing['id']})
            
        c.execute('''
            INSERT INTO users (
                name, age, sex, height, weight, target_weight, activity_level, diet_pref,
                budget, target_calories, tdee, macros, diet_plan, workout_type, mobile,
                email, google_id, auth_provider, avatar_url, is_profile_completed
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            profile.get('name'), profile.get('age'), profile.get('sex'), profile.get('height'), 
            profile.get('weight'), profile.get('target_weight'), profile.get('activity_level'), 
            profile.get('diet_pref'), profile.get('budget'), profile.get('target_calories'), 
            profile.get('tdee'), json.dumps(profile.get('macros', {})),
            json.dumps(profile.get('diet_plan')) if profile.get('diet_plan') else None,
            profile.get('workout_type'), profile.get('mobile'), profile.get('email'),
            profile.get('google_id'), profile.get('auth_provider'), profile.get('avatar_url'),
            1 if is_completed else 0
        ))
        user_id = c.lastrowid
        
    conn.commit()
    conn.close()
    return get_user_by_id(user_id)

def update_user_diet_plan(diet_plan, user_id=None):
    conn = get_connection()
    c = conn.cursor()
    if user_id:
        c.execute("UPDATE users SET diet_plan = ? WHERE id = ?", (json.dumps(diet_plan), user_id))
    else:
        c.execute("UPDATE users SET diet_plan = ? WHERE id = (SELECT id FROM users ORDER BY id DESC LIMIT 1)", (json.dumps(diet_plan),))
    conn.commit()
    conn.close()

# --- Daily Logs Methods ---
def get_daily_log():
    today_str = datetime.date.today().isoformat()
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM daily_logs WHERE date = ?", (today_str,))
    row = c.fetchone()
    conn.close()
    
    if row:
        return dict(row)
    else:
        # Create an empty log for today
        log = {'date': today_str, 'calories': 0, 'protein': 0, 'carbs': 0, 'fats': 0, 'water': 0}
        update_daily_log(log)
        return log

def update_daily_log(log):
    today_str = datetime.date.today().isoformat()
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO daily_logs (date, calories, protein, carbs, fats, water)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(date) DO UPDATE SET
            calories = excluded.calories,
            protein = excluded.protein,
            carbs = excluded.carbs,
            fats = excluded.fats,
            water = excluded.water
    ''', (
        today_str, log.get('calories', 0), log.get('protein', 0), 
        log.get('carbs', 0), log.get('fats', 0), log.get('water', 0)
    ))
    conn.commit()
    conn.close()

# --- Family Methods ---
def get_family_members():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM family_members")
    rows = c.fetchall()
    conn.close()
    
    members = []
    for row in rows:
        m = dict(row)
        m['stats'] = json.loads(m['stats']) if m['stats'] else {"calories": 0, "protein": 0, "carbs": 0, "fats": 0}
        members.append(m)
    return members

def add_family_member(member):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO family_members (name, relation, age, sex, weight, activity, stats)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        member.get('name'), member.get('relation'), member.get('age'), 
        member.get('sex'), member.get('weight'), member.get('activity'), 
        json.dumps(member.get('stats', {"calories": 0, "protein": 0, "carbs": 0, "fats": 0}))
    ))
    conn.commit()
    conn.close()

def update_family_member_stats(member_id, stats):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE family_members SET stats = ? WHERE id = ?", (json.dumps(stats), member_id))
    conn.commit()
    conn.close()

def delete_family_member(member_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM family_members WHERE id = ?", (member_id,))
    conn.commit()
    conn.close()

# --- Chat Methods ---
def get_chat_history():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT role, content FROM chat_history ORDER BY timestamp ASC")
    rows = c.fetchall()
    conn.close()
    return [{"role": row["role"], "content": row["content"]} for row in rows]

def add_chat_message(role, content):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO chat_history (role, content) VALUES (?, ?)", (role, content))
    conn.commit()
    conn.close()

def clear_chat_history():
    """Clear all chat messages from the database."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM chat_history")
    conn.commit()
    conn.close()
