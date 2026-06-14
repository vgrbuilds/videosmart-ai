from bson import ObjectId
from fastapi import HTTPException, status
from app.core.security import hash_password
from app.db.mongodb import get_users_collection
from app.schemas.auth import UserUpdate

class AuthProfileService:
    @staticmethod
    async def update_profile(user_id: str, user_update: UserUpdate, current_user: dict) -> dict:
        users_collection = get_users_collection()
        update_data = {}
        if user_update.username is not None:
            update_data["username"] = user_update.username
            
        if user_update.email is not None:
            if user_update.email != current_user["email"]:
                existing = await users_collection.find_one({"email": user_update.email})
                if existing:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Email already in use by another account."
                    )
                update_data["email"] = user_update.email
                
        if user_update.password is not None:
            update_data["password"] = hash_password(user_update.password)
            
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update were provided."
            )
            
        await users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data}
        )
        updated = await users_collection.find_one({"_id": ObjectId(user_id)})
        return {
            "id": str(updated["_id"]),
            "username": updated["username"],
            "email": updated["email"],
            "created_at": updated["created_at"]
        }

auth_profile_service = AuthProfileService()
