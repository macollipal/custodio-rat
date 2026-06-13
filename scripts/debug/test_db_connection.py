"""
Test connection to Neon database.
Usage: python test_db_connection.py
"""

import psycopg2

DATABASE_URL = "postgresql://neondb_owner:npg_Rem3X0tGwUxv@ep-flat-rice-aqay71bf-pooler.c-8.us-east-1.aws.neon.tech/Custodio_dev?sslmode=require&channel_binding=require"

def test_connection():
    try:
        host = DATABASE_URL.split('@')[1]
        print(f"Connecting to: {host}")
        conn = psycopg2.connect(DATABASE_URL)
        print("SUCCESS - Connection successful!")
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"PostgreSQL version: {version[0]}")
        cursor.execute("SELECT current_database();")
        db_name = cursor.fetchone()
        print(f"Current database: {db_name[0]}")
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"FAILED - Connection failed: {e}")
        return False

if __name__ == "__main__":
    test_connection()