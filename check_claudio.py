import psycopg2
import bcrypt
import sys

DATABASE_URL = "postgresql://neondb_owner:npg_RVH63hjIvwAD@ep-fragrant-wildflower-apeqosx9-pooler.c-7.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("SELECT id, username, hashed_password FROM users WHERE username IN ('claudio_admin', 'claudio_usr')")
    rows = cur.fetchall()

    for r in rows:
        username, stored_hash = r[1], r[2]
        # Test common passwords
        found = False
        for pwd in ['claudio_admin', 'claudio_usr', username, 'Admin1234!', 'Password123', 'claudio']:
            if bcrypt.checkpw(pwd.encode(), stored_hash.encode()):
                print(f"[OK] {username} -> password matches: '{pwd}'")
                found = True
                break
        if not found:
            print(f"[FAIL] {username} -> none of the test passwords matched")
    cur.close()
    conn.close()
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)