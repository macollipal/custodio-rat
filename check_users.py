import sqlite3
conn = sqlite3.connect('backend/data/database.db')
cursor = conn.cursor()
cursor.execute("SELECT id, username, rol_global, is_admin FROM users WHERE username LIKE '%claudio%'")
for row in cursor.fetchall():
    print(f'ID: {row[0]}, username: {row[1]}, rol: {row[2]}, is_admin: {row[3]}')
conn.close()