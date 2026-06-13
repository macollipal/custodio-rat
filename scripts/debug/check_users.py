import psycopg2
import bcrypt
import sys

DATABASE_URL = "postgresql://neondb_owner:npg_RVH63hjIvwAD@ep-fragrant-wildflower-apeqosx9-pooler.c-7.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

def try_common_passwords(username, stored_hash):
    """Try common passwords that match username pattern"""
    candidates = [
        username,
        username.replace('_', ''),
        username.replace('_user', ''),
        username.replace('_usr', ''),
        username.split('_')[0] if '_' in username else username,
        'Admin1234!',
        'Password123',
        'Usuario123',
    ]
    for pwd in candidates:
        try:
            if bcrypt.checkpw(pwd.encode(), stored_hash.encode()):
                return pwd
        except:
            pass
    return None

try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("SELECT id, username, email, hashed_password, rol_global FROM users ORDER BY id")
    rows = cur.fetchall()

    print("=== USERS PASSWORD CHECK ===")
    fixed = []

    for r in rows:
        user_id, username, email, stored_hash, rol = r
        matched = try_common_passwords(username, stored_hash)
        if matched:
            print(f"[OK] {username} ({rol}) - password: '{matched}'")
        else:
            print(f"[FAIL] {username} ({rol}) - password does NOT match common patterns")
            # Fix it - use username as password
            new_hash = bcrypt.hashpw(username.encode(), bcrypt.gensalt()).decode('utf-8')
            cur.execute("UPDATE users SET hashed_password = %s WHERE id = %s", (new_hash, user_id))
            fixed.append(username)
            print(f"      -> Fixed: password set to '{username}'")

    if fixed:
        conn.commit()
        print(f"\n=== FIXED {len(fixed)} users ===")

    cur.close()
    conn.close()
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)