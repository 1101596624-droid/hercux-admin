import sqlite3

conn = sqlite3.connect('hercu_dev.db')
cursor = conn.cursor()

# Get all tables
print('Database tables:')
cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
for row in cursor.fetchall():
    print(f'  {row[0]}')

# Check user_courses table
print('\nuser_courses table:')
cursor.execute('SELECT * FROM user_courses')
rows = cursor.fetchall()
if rows:
    for row in rows:
        print(f'  {row}')
else:
    print('  (empty)')

# Check learning_progress table
print('\nlearning_progress table (first 5):')
cursor.execute('SELECT id, user_id, node_id, status FROM learning_progress LIMIT 5')
rows = cursor.fetchall()
if rows:
    for row in rows:
        print(f'  ID: {row[0]}, User: {row[1]}, Node: {row[2]}, Status: {row[3]}')
else:
    print('  (empty)')

conn.close()
