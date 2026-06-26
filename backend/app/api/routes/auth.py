from operator import or_

from fastapi import APIRouter, Depends, status, HTTPException, Response
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from psycopg2 import IntegrityError
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import Book , User
from app.schemas.user import TokenResponse, UserCreate, UserOut, UserUpdate, UserLogin
from app.api.routes.users import hash_password, verify_password
from app.auth2 import create_access_token

router = APIRouter(tags=['Authentication'])

@router.post("/login")
def login(user_login: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == user_login.username).first()
    if not user or not verify_password(user_login.password, user.password_hash): # this compares the provided password with the hashed password stored in the database
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )       
    # create token
    # return token
    access_token = create_access_token(data={"user_id": str(user.id), "username": user.username})
    # return {"token" : access_token, "token_type": "bearer"} -  this i did before
    return {"access_token": access_token, "token_type": "bearer"}

@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED
)
def register(
    user_in: UserCreate,
    db: Session = Depends(get_db)
):
    existing_user = db.query(User).filter(
        or_(
            User.username == user_in.username,
            User.email == user_in.email
        )
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="Username or email already exists"
        )

    user = User(
        username=user_in.username,
        email=user_in.email,
        password_hash=hash_password(user_in.password),
        address=user_in.address,
        is_private=user_in.is_private,
        avatar_url=user_in.avatar_url,
        role="user"
    )

    try:
        db.add(user)
        db.commit()
        db.refresh(user)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Username or email already exists"
        )

    token = create_access_token(
        data={
            "user_id": str(user.id),
            "username": user.username,
            "role": user.role
        }
    )

    return {
        "token": token,
        "token_type": "bearer"
    }