# File: /my-fastapi-app/my-fastapi-app/app/services/user_service.py

# This file contains business logic related to user operations.

from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate

def create_user(db: Session, user: UserCreate) -> User:
    """
    Create a new user in the database.

    Args:
        db (Session): The database session.
        user (UserCreate): The user data to create.

    Returns:
        User: The created user instance.
    """
    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user(db: Session, user_id: int) -> User:
    """
    Retrieve a user by ID.

    Args:
        db (Session): The database session.
        user_id (int): The ID of the user to retrieve.

    Returns:
        User: The user instance if found, otherwise None.
    """
    return db.query(User).filter(User.id == user_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 10) -> list[User]:
    """
    Retrieve a list of users.

    Args:
        db (Session): The database session.
        skip (int): The number of users to skip.
        limit (int): The maximum number of users to return.

    Returns:
        list[User]: A list of user instances.
    """
    return db.query(User).offset(skip).limit(limit).all()