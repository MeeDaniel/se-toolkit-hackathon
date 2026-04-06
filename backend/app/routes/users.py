from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from passlib.context import CryptContext

from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserResponse, UserLogin, UserSetPassword, UserChangePassword

router = APIRouter()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


@router.post("/", response_model=UserResponse)
async def create_or_get_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new user or return existing one (case-insensitive)"""
    # Normalize to lowercase for case-insensitive matching
    normalized_alias = user_data.telegram_alias.lower()
    
    result = await db.execute(
        select(User).where(User.telegram_alias == normalized_alias)
    )
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        # Return existing user with password_protected flag
        return UserResponse(
            id=existing_user.id,
            telegram_alias=existing_user.telegram_alias,
            excursions=existing_user.excursions,
            password_protected=existing_user.password_hash is not None,
            created_at=existing_user.created_at
        )
    
    # Create new user (no password - web-only access)
    db_user = User(telegram_alias=normalized_alias, password_hash=None)
    db.add(db_user)
    await db.flush()
    await db.refresh(db_user)
    
    return UserResponse(
        id=db_user.id,
        telegram_alias=db_user.telegram_alias,
        excursions=db_user.excursions,
        password_protected=False,
        created_at=db_user.created_at
    )


@router.post("/login", response_model=UserResponse)
async def login_user(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db),
):
    """Login with alias and password (if required)"""
    normalized_alias = login_data.telegram_alias.lower()
    
    result = await db.execute(
        select(User).where(User.telegram_alias == normalized_alias)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found. Please register first.")
    
    # If user has password set, verify it
    if user.password_hash:
        if not login_data.password:
            raise HTTPException(status_code=401, detail="Password required for this account")
        if not verify_password(login_data.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid password")
    
    return UserResponse(
        id=user.id,
        telegram_alias=user.telegram_alias,
        excursions=user.excursions,
        password_protected=user.password_hash is not None,
        created_at=user.created_at
    )


@router.get("/{telegram_alias}", response_model=UserResponse)
async def get_user(
    telegram_alias: str,
    db: AsyncSession = Depends(get_db),
):
    """Get user by telegram alias"""
    normalized_alias = telegram_alias.lower()
    result = await db.execute(
        select(User).where(User.telegram_alias == normalized_alias)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse(
        id=user.id,
        telegram_alias=user.telegram_alias,
        excursions=user.excursions,
        password_protected=user.password_hash is not None,
        created_at=user.created_at
    )


@router.post("/set-password", response_model=dict)
async def set_user_password(
    data: UserSetPassword,
    db: AsyncSession = Depends(get_db),
):
    """Set password for a user (called from Telegram - no verification needed)"""
    normalized_alias = data.telegram_alias.lower()
    
    result = await db.execute(
        select(User).where(User.telegram_alias == normalized_alias)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Set new password
    user.password_hash = hash_password(data.password)
    await db.flush()
    
    return {"message": "Password set successfully", "password_protected": True}


@router.post("/change-password", response_model=dict)
async def change_user_password(
    data: UserChangePassword,
    db: AsyncSession = Depends(get_db),
):
    """Change user password (called from Telegram - no verification needed)"""
    normalized_alias = data.telegram_alias.lower()
    
    result = await db.execute(
        select(User).where(User.telegram_alias == normalized_alias)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update password
    user.password_hash = hash_password(data.new_password)
    await db.flush()
    
    return {"message": "Password changed successfully"}


@router.post("/remove-password", response_model=dict)
async def remove_user_password(
    telegram_alias: str,
    db: AsyncSession = Depends(get_db),
):
    """Remove password protection (called from Telegram)"""
    normalized_alias = telegram_alias.lower()
    
    result = await db.execute(
        select(User).where(User.telegram_alias == normalized_alias)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Remove password
    user.password_hash = None
    await db.flush()
    
    return {"message": "Password removed successfully", "password_protected": False}
