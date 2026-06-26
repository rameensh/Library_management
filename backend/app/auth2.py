from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.schemas.user import TokenData
from app.core.database import get_db
from app.models.models import User
from app.core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

Oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = SECRET_KEY
ALGORITHM = ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = ACCESS_TOKEN_EXPIRE_MINUTES

def create_access_token(data: dict):
    to_encode = data.copy()
    # now we will have to add an expiration time 
    # to the token. This is a common practice to ensure that tokens are only valid for a certain period of time.
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# api will use this function to verify the token and get the user information from it.
# any api endpoint that requires authentication will use this function to get the current user.
# def verify_token(token: str, credentials_exception):
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         user_id: str = payload.get("user_id")
#         username: str = payload.get("username")
#         if user_id is None or username is None:
#             raise credentials_exception
#         token_data = TokenData(user_id=user_id, username=username)
#     except JWTError:
#         raise credentials_exception
#     return token_data

def verify_token(token: str, credentials_exception):
    try:
        print("TOKEN RECEIVED:", token)

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        print("PAYLOAD:", payload)

        user_id: str = payload.get("user_id")
        username: str = payload.get("username")

        if user_id is None or username is None:
            raise credentials_exception

        token_data = TokenData(
            user_id=user_id,
            username=username
        )

    except JWTError as e:
        print("JWT ERROR:", e)
        raise credentials_exception

    return token_data

# Now we will create a function that will be used as a dependency in our API 
# endpoints to get the current user from the token.
# This function will take the token from the  request automatically and verify it using the verify_token function. 
# If the token is valid, it will return the user information from the token.
def get_current_user(
    Token: str = Depends(Oauth2_scheme),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data = verify_token(Token, credentials_exception)

    user = (
        db.query(User)
        .filter(User.id == token_data.user_id)
        .first()
    )

    if not user:
        raise credentials_exception

    return user

