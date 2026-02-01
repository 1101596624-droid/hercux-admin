import sqlite3
conn = sqlite3.connect('hercu_dev.db')
cursor = conn.cursor()
cursor.execute('SELECT email FROM users')
for row in cursor.fetchall():
    print(row[0])
conn.close()
