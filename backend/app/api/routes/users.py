import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import User
from app.schemas.user import UserCreate, UserOut, UserUpdate
from app.auth2 import get_current_user
import bcrypt


router = APIRouter(prefix="/api/users", tags=["users"])

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))

@router.post("", response_model=UserOut)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(
        or_(User.username == user_in.username, User.email == user_in.email)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username or email already exists")

    user = User(
        username=user_in.username,
        email=user_in.email,
        password_hash=hash_password(user_in.password), 
        address=user_in.address,
        is_private=user_in.is_private,
        avatar_url=user_in.avatar_url,
        role="user"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.get("", response_model=List[UserOut])
def list_users(
    db: Session = Depends(get_db),
    search: Optional[str] = Query(None, description="Search by username or email")
):
    query = db.query(User)
    if search:
        query = query.filter(
            or_(User.username.contains(search), User.email.contains(search))
        )
    return query.all()

# ✅ THIS IS THE CORRECT ENDPOINT - Add this exactly:
@router.get("/me", response_model=UserOut)
def get_current_user_profile(
    current_user: User = Depends(get_current_user),
):
    """
    Get the profile of the currently authenticated user.
    Uses the JWT token to identify the user.
    """
    if not current_user:
        raise HTTPException(status_code=404, detail="User not found")
    return current_user

@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: uuid.UUID, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=UserOut)
def update_user(user_id: uuid.UUID, user_in: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user_in.username is not None: user.username = user_in.username
    if user_in.email is not None: user.email = user_in.email
    if user_in.password is not None: user.password_hash = hash_password(user_in.password)
    if user_in.address is not None: user.address = user_in.address
    if user_in.is_private is not None: user.is_private = user_in.is_private
    if user_in.avatar_url is not None: user.avatar_url = user_in.avatar_url

    db.commit()
    db.refresh(user)
    return user

@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: uuid.UUID, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return