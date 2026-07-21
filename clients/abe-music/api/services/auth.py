import os
import hashlib
import jwt
from datetime import datetime, timedelta, timezone
from database import query_db

SECRET = os.environ.get("ABE_JWT_SECRET", "abe-dev-secret-2026")

class AuthService:
    @staticmethod
    def hash_password(password: str, salt: str = None) -> tuple:
        if not salt:
            salt = hashlib.sha256(os.urandom(32)).hexdigest()[:16]
        hashed = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100000).hex()
        return salt, hashed

    @staticmethod
    def verify_password(password: str, stored: str) -> bool:
        salt, hashed = stored.split(":")
        _, computed = AuthService.hash_password(password, salt)
        return computed == hashed

    @staticmethod
    def create_token(email: str, role: str, name: str) -> str:
        return jwt.encode({
            "email": email,
            "role": role,
            "name": name,
            "exp": datetime.now(timezone.utc) + timedelta(days=7)
        }, SECRET, algorithm="HS256")

    @staticmethod
    def decode_token(token: str) -> dict:
        return jwt.decode(token, SECRET, algorithms=["HS256"])

    @staticmethod
    def find_user(email: str):
        rows = query_db("SELECT id, name, email, password_hash, role FROM users WHERE email = :email", {"email": email})
        return rows[0] if rows else None

    @staticmethod
    def find_user_by_id(user_id: str):
        rows = query_db("SELECT id, name, email, role, avatar, telegram_id FROM users WHERE id = :id", {"id": user_id})
        return rows[0] if rows else None

    @staticmethod
    def create_user(name: str, email: str, password: str, role: str = "user"):
        salt, hashed = AuthService.hash_password(password)
        query_db(
            "INSERT INTO users (name, email, password_hash, role) VALUES (:name, :email, :phash, :role)",
            {"name": name, "email": email, "phash": f"{salt}:{hashed}", "role": role}
        )
        return AuthService.find_user(email)
