from pydantic import BaseModel
from typing import Optional

# User schema for creating a new user
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

# User schema for returning user data
class User(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        orm_mode = True

# User schema for updating user data
class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None