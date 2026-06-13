"""
Reset admin password to 'Admin1234!' using bcrypt
Run: python reset_admin.py
"""

import psycopg2
from passlib.context import CryptContext

DATABASE_URL = "postgresql://neondb_owner:npg_Rem3X0tGwUxv@ep-flat-rice-aqay71bf-pooler.c-8.us-east-1.aws.neon.tech/Custodio_dev?sslmode=require&channel_binding=require"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def main():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    cursor.execute("SELECT id, username FROM users WHERE username = 'admin';")
    admin = cursor.fetchone()

    if admin:
        print(f"Admin user found: ID={admin[0]}, username={admin[1]}")
        new_password = "Admin1234!"
        hashed = pwd_context.hash(new_password)
        print(f"New hash: {hashed[:50]}...")
        cursor.execute("UPDATE users SET hashed_password = %s WHERE username = 'admin';", (hashed,))
        conn.commit()
        print("Password updated to 'Admin1234!'")
    else:
        print("Admin user not found!")

    conn.close()

if __name__ == "__main__":
    main()