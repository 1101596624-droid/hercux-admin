"""
Security utilities for JWT authentication and password hashing
"""
from datetime import datetime, timedelta, timezone
from typing import Literal, Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, Header, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.db.session import get_db
from app.models.models import User

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_PREFIX}/auth/login")

# Optional OAuth2 scheme (doesn't raise error if no token)
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_PREFIX}/auth/login", auto_error=False)

ClientType = Literal["desktop", "app", "admin", "unknown"]


def normalize_client_type(client_type: Optional[str]) -> ClientType:
    """
    Normalize raw client type from request headers / token claims.
    """
    if not client_type:
        return "unknown"

    value = client_type.strip().lower()
    alias_map = {
        "student": "desktop",
        "web": "desktop",
        "main": "app",
        "mobile": "app",
        "android": "app",
        "ios": "app",
        "management": "admin",
        "backoffice": "admin",
    }
    value = alias_map.get(value, value)

    if value in {"desktop", "app", "admin"}:
        return value  # type: ignore[return-value]

    return "unknown"


def decode_token(token: str) -> dict:
    """
    Decode JWT token payload.
    """
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])


def get_client_type_from_token(token: Optional[str]) -> ClientType:
    """
    Parse client_type claim from JWT token.
    """
    if not token:
        return "unknown"

    try:
        payload = decode_token(token)
    except JWTError:
        return "unknown"

    return normalize_client_type(payload.get("client_type"))


async def get_request_client_type(
    token: Optional[str] = Depends(oauth2_scheme_optional),
    x_client_type: Optional[str] = Header(None, alias="X-Client-Type")
) -> ClientType:
    """
    Resolve request client type with priority:
    1) X-Client-Type header
    2) JWT client_type claim
    """
    header_client_type = normalize_client_type(x_client_type)
    if header_client_type != "unknown":
        return header_client_type

    return get_client_type_from_token(token)


async def require_non_app_client(
    client_type: ClientType = Depends(get_request_client_type)
) -> ClientType:
    """
    Guard for endpoints that should not be used by APP clients.
    """
    if client_type == "app":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="当前接口仅桌面端/后台开放，APP 端请使用 Universe 业务能力。"
        )
    return client_type


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token

    Args:
        data: Dictionary containing the claims to encode in the token
        expires_delta: Optional expiration time delta

    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    return encoded_jwt


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Get the current authenticated user from JWT token

    Args:
        token: JWT token from Authorization header
        db: Database session

    Returns:
        User object

    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode JWT token
        payload = decode_token(token)
        user_id_str: str = payload.get("sub")

        if user_id_str is None:
            raise credentials_exception

        # Convert string user_id back to integer
        try:
            user_id = int(user_id_str)
        except (ValueError, TypeError):
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    # Get user from database
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get the current active user

    Args:
        current_user: Current user from get_current_user dependency

    Returns:
        User object

    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


async def get_current_premium_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get the current premium user

    Args:
        current_user: Current user from get_current_user dependency

    Returns:
        User object

    Raises:
        HTTPException: If user is not premium
    """
    if not current_user.is_premium:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Premium subscription required"
        )
    return current_user


async def get_current_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get the current admin user

    Args:
        current_user: Current user from get_current_user dependency

    Returns:
        User object

    Raises:
        HTTPException: If user is not an admin
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user


# Alias for convenience
require_admin = get_current_admin_user


async def authenticate_user(db: AsyncSession, email: str, password: str) -> Optional[User]:
    """
    Authenticate a user by email and password

    Args:
        db: Database session
        email: User email
        password: Plain text password

    Returns:
        User object if authentication successful, None otherwise
    """
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user


async def get_current_user_optional(
    token: Optional[str] = Depends(oauth2_scheme_optional),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """
    Get the current user if authenticated, otherwise return None.
    This is useful for endpoints that work for both authenticated and anonymous users.

    Args:
        token: Optional JWT token from Authorization header
        db: Database session

    Returns:
        User object if authenticated, None otherwise
    """
    if not token:
        return None

    try:
        payload = decode_token(token)
        user_id_str: str = payload.get("sub")

        if user_id_str is None:
            return None

        try:
            user_id = int(user_id_str)
        except (ValueError, TypeError):
            return None

        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if user and user.is_active:
            return user

    except JWTError:
        pass

    return None
