import sqlite3

conn = sqlite3.connect('hercu_dev.db')
cursor = conn.cursor()

print('learning_progress table schema:')
cursor.execute('PRAGMA table_info(learning_progress)')
for row in cursor.fetchall():
    print(f'  {row[1]} ({row[2]})')

print('\nSample data:')
cursor.execute('SELECT * FROM learning_progress LIMIT 1')
columns = [description[0] for description in cursor.description]
print(f'Columns: {columns}')
row = cursor.fetchone()
if row:
    for i, col in enumerate(columns):
        print(f'  {col}: {row[i]}')

conn.close()
