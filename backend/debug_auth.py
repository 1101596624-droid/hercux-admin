from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from init_db import User
import os

db_path = os.environ.get('DB_PATH', '/www/wwwroot/hercu-backend/hercu.db')
engine = create_engine(f'sqlite:///{db_path}')
Session = sessionmaker(bind=engine)
session = Session()

# 查看用户
users = session.query(User).all()
for u in users:
    print(f"ID: {u.id}")
    print(f"Email: {u.email}")
    print(f"Hash: {u.hashed_password[:50]}...")
    print(f"Hash length: {len(u.hashed_password)}")
    print("---")

# 测试密码验证
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

test_hash = pwd_context.hash("admin123")
print(f"\nNew hash: {test_hash}")
print(f"New hash length: {len(test_hash)}")

# 验证
try:
    result = pwd_context.verify("admin123", test_hash)
    print(f"Verify new hash: {result}")
except Exception as e:
    print(f"Verify error: {e}")

# 验证数据库中的
if users:
    try:
        result = pwd_context.verify("admin123", users[0].hashed_password)
        print(f"Verify DB hash: {result}")
    except Exception as e:
        print(f"Verify DB error: {e}")
