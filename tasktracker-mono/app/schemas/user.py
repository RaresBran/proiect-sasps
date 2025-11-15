from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from typing import Optional


# Base User schema with common attributes
class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    full_name: Optional[str] = Field(None, max_length=255)


# Schema for user registration
class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=100)


# Schema for user login
class UserLogin(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=6, max_length=100)


# Schema for user update
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    full_name: Optional[str] = Field(None, max_length=255)
    password: Optional[str] = Field(None, min_length=6, max_length=100)


# Schema for user response (excludes sensitive data)
class UserResponse(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# Schema for user in database (includes hashed password)
class UserInDB(UserResponse):
    hashed_password: str
    
    model_config = ConfigDict(from_attributes=True)


# Schema for token response
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# Schema for token payload
class TokenPayload(BaseModel):
    sub: Optional[int] = None  # subject (user_id)
    exp: Optional[int] = None  # expiration time
    iat: Optional[int] = None  # issued at time

