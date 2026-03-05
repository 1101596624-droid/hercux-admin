"""
Authentication endpoints
"""
from datetime import timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr

from app.core.config import settings
from app.core.security import (
    authenticate_user,
    create_access_token,
    get_password_hash,
    get_client_type_from_token,
    get_current_user,
    normalize_client_type,
    oauth2_scheme,
)
from app.db.session import get_db
from app.models.models import User
from app.schemas.schemas import Token, UserCreate, UserResponse
from app.services.email_service import send_code_to_email, verify_code

router = APIRouter()


class SendCodeRequest(BaseModel):
    """Request model for sending verification code"""
    email: EmailStr
    purpose: str = "register"  # register, reset_password, change_email


class SendCodeResponse(BaseModel):
    """Response model for send code"""
    success: bool
    message: str


class RegisterWithCodeRequest(BaseModel):
    """Request model for registration with verification code"""
    email: EmailStr
    password: str
    verification_code: str


class ResetPasswordRequest(BaseModel):
    """Request model for password reset"""
    email: EmailStr
    password: str
    verification_code: str


@router.post("/send-code", response_model=SendCodeResponse)
async def send_verification_code(
    request: SendCodeRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Send verification code to email

    Args:
        request: Email and purpose
        db: Database session

    Returns:
        Success status and message
    """
    # For registration, check if email already exists
    if request.purpose == "register":
        result = await db.execute(select(User).where(User.email == request.email))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该邮箱已被注册"
            )

    # For password reset, check if email exists
    if request.purpose == "reset_password":
        result = await db.execute(select(User).where(User.email == request.email))
        if not result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该邮箱未注册"
            )

    # Send verification code
    success, message = await send_code_to_email(request.email, request.purpose)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=message
        )

    return SendCodeResponse(success=True, message=message)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterWithCodeRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user with email verification code

    Args:
        request: Registration data with verification code
        db: Database session

    Returns:
        Created user object

    Raises:
        HTTPException: If email already exists or verification fails
    """
    # 检查是否允许注册
    from app.core.system_settings import get_user_settings
    user_settings = get_user_settings()
    if not user_settings.allow_registration:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="注册功能已关闭，请联系管理员"
        )

    # Verify the code
    is_valid, error_message = verify_code(request.email, request.verification_code, "register")
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )

    # Check if email already exists
    result = await db.execute(select(User).where(User.email == request.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该邮箱已被注册"
        )

    # Generate username from email (part before @)
    username = request.email.split('@')[0]
    # Check if username exists, if so, add random suffix
    result = await db.execute(select(User).where(User.username == username))
    if result.scalar_one_or_none():
        import random
        import string
        username = username + '_' + ''.join(random.choices(string.digits, k=4))

    # Create new user
    user = User(
        email=request.email,
        username=username,
        hashed_password=get_password_hash(request.password),
        full_name=username,  # Default full_name to username
        is_active=1,
        is_premium=0
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user


@router.post("/reset-password", response_model=SendCodeResponse)
async def reset_password(
    request: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Reset password with email verification code

    Args:
        request: Email, new password and verification code
        db: Database session

    Returns:
        Success status and message
    """
    # Verify the code
    is_valid, error_message = verify_code(request.email, request.verification_code, "reset_password")
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )

    # Find user
    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该邮箱未注册"
        )

    # Update password
    user.hashed_password = get_password_hash(request.password)
    await db.commit()

    return SendCodeResponse(success=True, message="密码重置成功")


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
    x_client_type: Optional[str] = Header(None, alias="X-Client-Type")
):
    """
    Login with email and password to get access token

    Args:
        form_data: OAuth2 form data (username field contains email)
        db: Database session
        x_client_type: Client type header ("desktop"/"app"/"admin")

    Returns:
        Access token and token type

    Raises:
        HTTPException: If credentials are invalid
    """
    # 检查账号是否被锁定
    from app.services.login_lock_service import check_login_lock, record_login_failure, clear_login_failures
    is_locked, lock_message = check_login_lock(form_data.username)
    if is_locked:
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=lock_message
        )

    # Authenticate user (username field contains email)
    user = await authenticate_user(db, form_data.username, form_data.password)

    if not user:
        # 记录登录失败
        is_now_locked, fail_message = record_login_failure(form_data.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=fail_message or "Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 登录成功，清除失败记录
    clear_login_failures(form_data.username)

    # 根据客户端类型设置不同的有效期
    # desktop: 7天, app: 7天, admin: 3天
    client_type = normalize_client_type(x_client_type)
    if client_type == "desktop":
        expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES_DESKTOP
    elif client_type == "app":
        expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES_APP
    elif client_type == "admin":
        expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES_ADMIN
    else:
        expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES

    access_token_expires = timedelta(minutes=expire_minutes)
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "client_type": client_type,
        },
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": expire_minutes * 60  # 转换为秒
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user information

    Args:
        current_user: Current user from JWT token

    Returns:
        Current user object
    """
    return current_user


@router.post("/refresh", response_model=Token)
async def refresh_token(
    current_user: User = Depends(get_current_user),
    token: str = Depends(oauth2_scheme),
    x_client_type: Optional[str] = Header(None, alias="X-Client-Type")
):
    """
    Refresh access token

    Args:
        current_user: Current user from JWT token
        x_client_type: Client type header ("desktop"/"app"/"admin")

    Returns:
        New access token and token type
    """
    # 优先使用请求头，缺省时回落到现有 token 的 client_type claim
    client_type = normalize_client_type(x_client_type)
    if client_type == "unknown":
        client_type = get_client_type_from_token(token)

    if client_type == "desktop":
        expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES_DESKTOP
    elif client_type == "app":
        expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES_APP
    elif client_type == "admin":
        expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES_ADMIN
    else:
        expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES

    access_token_expires = timedelta(minutes=expire_minutes)
    access_token = create_access_token(
        data={
            "sub": str(current_user.id),
            "client_type": client_type,
        },
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": expire_minutes * 60  # 转换为秒
    }
