import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

class UserBase(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    email: str = Field(..., min_length=1, max_length=100)
    address: Optional[str] = Field(None, max_length=200)
    is_private: bool = False
    avatar_url: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128)

class UserOut(UserBase):
    id: uuid.UUID
    role: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=1, max_length=50)
    email: Optional[str] = Field(None, min_length=1, max_length=100)
    password: Optional[str] = Field(None, min_length=8, max_length=128)
    address: Optional[str] = Field(None, max_length=200)
    is_private: Optional[bool] = None
    avatar_url: Optional[str] = None

class UserLogin(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=8, max_length=128)

class TokenResponse(BaseModel):
    token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: Optional[str] = None
    username: Optional[str] = None