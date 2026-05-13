import os, sqlite3
os.chdir('C:/Users/chelo/Desktop/RAT_opencode/backend')
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

cursor.execute("SELECT id, username, rol_global, is_active FROM users")
print("Users:")
for row in cursor.fetchall():
    print(f"  {row}")

cursor.execute("SELECT id, nombre FROM companies")
print("\nCompanies:")
for row in cursor.fetchall():
    print(f"  {row}")

cursor.execute("SELECT id, username, company_id, rol FROM user_companies")
print("\nUser-Companies:")
for row in cursor.fetchall():
    print(f"  {row}")

conn.close()