from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext
from init_db import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Use absolute path for Linux server
import os
db_path = os.environ.get('DB_PATH', '/www/wwwroot/hercu-backend/hercu.db')
engine = create_engine(f'sqlite:///{db_path}')
Session = sessionmaker(bind=engine)
session = Session()

# 先删除已存在的用户
session.query(User).filter(User.email.in_(['admin@hercu.com', 'demo@hercu.com', 'student@hercu.com'])).delete(synchronize_session=False)
session.commit()

# 管理员账户
admin = User(
    email='admin@hercu.com',
    username='admin',
    hashed_password=pwd_context.hash('admin123'),
    full_name='Admin',
    is_admin=True,
    is_active=True
)

# 学生测试账户
demo = User(
    email='demo@hercu.com',
    username='demo',
    hashed_password=pwd_context.hash('demo123'),
    full_name='Demo User',
    is_admin=False,
    is_active=True
)

student = User(
    email='student@hercu.com',
    username='student',
    hashed_password=pwd_context.hash('student123'),
    full_name='Student User',
    is_admin=False,
    is_active=True
)

session.add_all([admin, demo, student])
session.commit()
print(f'Database: {db_path}')
print('Users created!')
print('Admin: admin@hercu.com / admin123')
print('Demo: demo@hercu.com / demo123')
print('Student: student@hercu.com / student123')
