import psycopg2
import bcrypt
import sys

DATABASE_URL = "postgresql://neondb_owner:npg_RVH63hjIvwAD@ep-fragrant-wildflower-apeqosx9-pooler.c-7.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    users = [
        ('claudio_admin', 'claudio_admin'),
        ('claudio_usr', 'claudio_usr'),
    ]

    for username, password in users:
        new_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode('utf-8')
        cur.execute(
            "UPDATE users SET hashed_password = %s WHERE username = %s",
            (new_hash, username)
        )
        print(f"[OK] {username} password updated")

    conn.commit()
    cur.close()
    conn.close()
    print("Done!")
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)