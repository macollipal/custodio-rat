import os, sqlite3
os.chdir('C:/Users/chelo/Desktop/RAT_opencode/backend')
conn = sqlite3.connect('database.db')
cursor = conn.cursor()
cursor.execute("UPDATE users SET rol_global='superadmin' WHERE username='admin'")
conn.commit()
print('Updated:', cursor.rowcount)
cursor.execute('SELECT id, username, rol_global FROM users')
for row in cursor.fetchall():
    print(row)
conn.close()