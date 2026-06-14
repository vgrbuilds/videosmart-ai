from datetime import datetime, timedelta
from fastapi import HTTPException, status
from app.core.config import settings
from app.core.security import hash_password, verify_password, create_access_token
from app.db.mongodb import get_users_collection
from app.schemas.auth import UserRegister, UserLogin

class AuthLoginService:
    @staticmethod
    async def register(user_in: UserRegister) -> dict:
        users_collection = get_users_collection()
        existing_user = await users_collection.find_one({"email": user_in.email})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this email already exists."
            )
            
        user_dict = {
            "username": user_in.username,
            "email": user_in.email,
            "password": hash_password(user_in.password),
            "created_at": datetime.utcnow()
        }
        result = await users_collection.insert_one(user_dict)
        return {
            "id": str(result.inserted_id),
            "username": user_dict["username"],
            "email": user_dict["email"],
            "created_at": user_dict["created_at"]
        }

    @staticmethod
    async def login(user_in: UserLogin) -> dict:
        users_collection = get_users_collection()
        user = await users_collection.find_one({"email": user_in.email})
        if not user or not verify_password(user_in.password, user["password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        token = create_access_token(subject=user["_id"], expires_delta=expires)
        return {"access_token": token, "token_type": "bearer"}

auth_login_service = AuthLoginService()
