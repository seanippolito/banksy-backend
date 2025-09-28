from fastapi import APIRouter, Depends
from app.api.deps import get_current_user
from app.schemas.user import UserRead
from app.db.models import User

router = APIRouter(prefix="/api/v1", tags=["users"])

@router.get("/me", response_model=UserRead)
async def read_me(user: User = Depends(get_current_user)):
    return user
