import time
from pymongo import MongoClient
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from app.core.config import settings
from app.db.mongodb import get_video_chunks_collection

VECTOR_INDEX_NAME = "vector_index"

class RobustGoogleEmbeddings(GoogleGenerativeAIEmbeddings):
    def _embed_retry(self, func, *args, **kwargs):
        last_exc = None
        for delay in [1, 2, 4]:
            try: return func(*args, **kwargs)
            except Exception as e:
                last_exc = e
                if any(x in str(e).lower() for x in ["500", "429", "internal"]):
                    time.sleep(delay)
                    continue
                raise e
        raise last_exc
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self._embed_retry(super().embed_documents, texts)
    def embed_query(self, text: str) -> list[float]:
        return self._embed_retry(super().embed_query, text)

def get_sync_video_chunks_collection():
    return MongoClient(settings.MONGO_URI)[settings.DATABASE_NAME]["video_chunks"]

def get_embeddings():
    return RobustGoogleEmbeddings(model="models/gemini-embedding-2", google_api_key=settings.GEMINI_API_KEY)

def build_vector_store(transcript: str, video_id: str) -> MongoDBAtlasVectorSearch:
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    docs = [Document(page_content=ch, metadata={'video_id': str(video_id), 'chunk_index': i})
            for i, ch in enumerate(splitter.split_text(transcript))]
    return MongoDBAtlasVectorSearch.from_documents(
        documents=docs, embedding=get_embeddings(),
        collection=get_sync_video_chunks_collection(), index_name=VECTOR_INDEX_NAME
    )

def load_vector_store() -> MongoDBAtlasVectorSearch:
    return MongoDBAtlasVectorSearch(
        collection=get_sync_video_chunks_collection(),
        embedding=get_embeddings(), index_name=VECTOR_INDEX_NAME
    )

def get_retriever(vector_store: MongoDBAtlasVectorSearch, video_id: str, k: int = 4):
    return vector_store.as_retriever(
        search_type='similarity',
        search_kwargs={"k": k, "pre_filter": {"video_id": str(video_id)}}
    )

async def delete_vector_store_chunks(video_id: str):
    res = await get_video_chunks_collection().delete_many({"video_id": str(video_id)})
    return res.deleted_count
