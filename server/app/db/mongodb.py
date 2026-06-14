from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class Database:
    client: AsyncIOMotorClient = None
    db = None

db_instance = Database()

async def connect_to_mongo():
    logger.info("Connecting to MongoDB...")
    db_instance.client = AsyncIOMotorClient(settings.MONGO_URI)
    db_instance.db = db_instance.client[settings.DATABASE_NAME]
    logger.info("Connected to MongoDB successfully!")

async def close_mongo_connection():
    logger.info("Closing connection to MongoDB...")
    if db_instance.client:
        db_instance.client.close()
    logger.info("Connection to MongoDB closed.")

def get_database():
    return db_instance.db

# Collection helpers
def get_users_collection():
    return db_instance.db["users"]

def get_videos_collection():
    return db_instance.db["videos"]

def get_video_chunks_collection():
    return db_instance.db["video_chunks"]

def get_conversations_collection():
    return db_instance.db["conversations"]
