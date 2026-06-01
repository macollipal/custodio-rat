"""
Test connection to Neon DB and check users.
Run: python test_users.py
"""

import psycopg2

DATABASE_URL = "postgresql://neondb_owner:npg_Rem3X0tGwUxv@ep-flat-rice-aqay71bf-pooler.c-8.us-east-1.aws.neon.tech/Custodio_dev?sslmode=require&channel_binding=require"

def main():
    print(f"Connecting to: {DATABASE_URL.split('@')[1]}")
    try:
        conn = psycopg2.connect(DATABASE_URL)
        print("Connected!")
        cursor = conn.cursor()

        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
        tables = cursor.fetchall()
        print(f"\nTables: {[t[0] for t in tables]}")

        cursor.execute("SELECT id, username, email, full_name, rol_global, is_active, is_admin FROM users LIMIT 10;")
        users = cursor.fetchall()
        print(f"\nUsers found: {len(users)}")
        for u in users:
            print(f"  ID={u[0]}, username={u[1]}, email={u[2]}, full_name={u[3]}, rol={u[4]}, active={u[5]}, admin={u[6]}")

        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()