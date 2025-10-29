"""
DianaBot - Security Utilities
"""
import hmac
import hashlib
import base64
from datetime import datetime, timedelta
from typing import Optional
import jwt
from passlib.context import CryptContext
from .settings import settings


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt


def verify_access_token(token: str) -> Optional[dict]:
    """Verify a JWT access token and return the payload"""
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        return payload
    except jwt.JWTError:
        return None


def create_secure_callback(data: dict) -> str:
    """
    Create callback data with security signature
    """
    import json
    payload_json = json.dumps(data, sort_keys=True)
    signature = hmac.new(
        settings.callback_secret.encode(),
        payload_json.encode(),
        hashlib.sha256
    ).hexdigest()[:16]
    
    # Create the actual data string
    data_str = base64.b64encode(payload_json.encode()).decode()
    
    return f"{signature}:{data_str}"


def verify_callback(callback_data: str) -> Optional[dict]:
    """
    Verify and decode callback data
    """
    import json
    try:
        signature, encoded_payload = callback_data.split(':', 1)
        payload_json = base64.b64decode(encoded_payload).decode()
        
        # Reconstruct expected signature
        expected_signature = hmac.new(
            settings.callback_secret.encode(),
            payload_json.encode(),
            hashlib.sha256
        ).hexdigest()[:16]
        
        if not hmac.compare_digest(signature, expected_signature):
            return None
        
        return json.loads(payload_json)
    except Exception:
        return None


def generate_callback_signature(data: str) -> str:
    """Generate HMAC signature for callback data"""
    return hmac.new(
        settings.callback_secret.encode(),
        data.encode(),
        hashlib.sha256
    ).hexdigest()


def verify_callback_signature(data: str, signature: str) -> bool:
    """Verify HMAC signature for callback data"""
    expected_signature = generate_callback_signature(data)
    return hmac.compare_digest(signature, expected_signature)