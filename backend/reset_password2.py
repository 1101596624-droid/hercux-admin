import sqlite3
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

test_hash = pwd_context.hash('test123')
admin_hash = pwd_context.hash('admin123')

conn = sqlite3.connect('hercu_dev.db')
cursor = conn.cursor()
cursor.execute('UPDATE users SET hashed_password = ? WHERE email = ?', (test_hash, 'test@hercu.com'))
cursor.execute('UPDATE users SET hashed_password = ? WHERE email = ?', (admin_hash, 'admin@hercu.com'))
conn.commit()
print('Done!')
print('test@hercu.com -> test123')
print('admin@hercu.com -> admin123')
conn.close()
