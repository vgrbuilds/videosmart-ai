from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from app.core.security import get_current_user
from app.services.auth_login import auth_login_service
from app.services.auth_profile import auth_profile_service
from app.schemas.auth import UserRegister, UserLogin, Token, UserOut, UserUpdate

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserRegister):
    return await auth_login_service.register(user_in)

@router.post("/login", response_model=Token)
async def login(user_in: UserLogin):
    return await auth_login_service.login(user_in)

@router.post("/login/form", response_model=Token, include_in_schema=False)
async def login_form(form_data: OAuth2PasswordRequestForm = Depends()):
    user_in = UserLogin(email=form_data.username, password=form_data.password)
    return await auth_login_service.login(user_in)

@router.get("/profile", response_model=UserOut)
async def get_profile(current_user: dict = Depends(get_current_user)):
    return current_user

@router.put("/profile", response_model=UserOut)
async def update_profile(
    user_update: UserUpdate,
    current_user: dict = Depends(get_current_user)
):
    return await auth_profile_service.update_profile(current_user["id"], user_update, current_user)
