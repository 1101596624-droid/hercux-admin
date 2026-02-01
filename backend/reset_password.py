import sqlite3
import bcrypt

test_hash = bcrypt.hashpw('test123'.encode(), bcrypt.gensalt()).decode()
admin_hash = bcrypt.hashpw('admin123'.encode(), bcrypt.gensalt()).decode()

conn = sqlite3.connect('hercu_dev.db')
cursor = conn.cursor()
cursor.execute('UPDATE users SET hashed_password = ? WHERE email = ?', (test_hash, 'test@hercu.com'))
cursor.execute('UPDATE users SET hashed_password = ? WHERE email = ?', (admin_hash, 'admin@hercu.com'))
conn.commit()
print('Done!')
print('test@hercu.com -> test123')
print('admin@hercu.com -> admin123')
conn.close()
