from pymongo import MongoClient
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from app.core.config import settings
from app.db.mongodb import get_video_chunks_collection

VECTOR_INDEX_NAME = "vector_index"

def get_sync_video_chunks_collection():
    client = MongoClient(settings.MONGO_URI)
    return client[settings.DATABASE_NAME]["video_chunks"]

def get_embeddings():
    return GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=settings.GEMINI_API_KEY
    )

def build_vector_store(transcript: str, video_id: str) -> MongoDBAtlasVectorSearch:
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = splitter.split_text(transcript)

    docs = [
        Document(
            page_content=chunk,
            metadata={'video_id': str(video_id), 'chunk_index': i}
        )
        for i, chunk in enumerate(chunks)
    ]

    vector_store = MongoDBAtlasVectorSearch.from_documents(
        documents=docs,
        embedding=get_embeddings(),
        collection=get_sync_video_chunks_collection(),
        index_name=VECTOR_INDEX_NAME
    )
    return vector_store

def load_vector_store() -> MongoDBAtlasVectorSearch:
    return MongoDBAtlasVectorSearch(
        collection=get_sync_video_chunks_collection(),
        embedding=get_embeddings(),
        index_name=VECTOR_INDEX_NAME
    )

def get_retriever(vector_store: MongoDBAtlasVectorSearch, video_id: str, k: int = 4):
    return vector_store.as_retriever(
        search_type='similarity',
        search_kwargs={
            "k": k,
            "pre_filter": {"video_id": str(video_id)}
        }
    )

async def delete_vector_store_chunks(video_id: str):
    collection = get_video_chunks_collection()
    result = await collection.delete_many({"video_id": str(video_id)})
    return result.deleted_count
