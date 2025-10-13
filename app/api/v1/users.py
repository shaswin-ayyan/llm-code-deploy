from fastapi import APIRouter, HTTPException
from app.schemas.user import UserCreate, UserResponse
from app.services.user_service import create_user

router = APIRouter()

@router.post("/users/", response_model=UserResponse)
async def register_user(user: UserCreate):
    """
    Create a new user.
    """
    try:
        new_user = await create_user(user)
        return new_user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))