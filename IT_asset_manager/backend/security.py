import bcrypt
from typing import Optional

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(stored_hash: str, entered_password: str) -> bool:
    """Verify a password against a stored hash"""
    try:
        return bcrypt.checkpw(
            entered_password.encode('utf-8'),
            stored_hash.encode('utf-8')
        )
    except ValueError:
        return False

