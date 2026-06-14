import uvicorn
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    print("Starting VideoSmart AI FastAPI Server on http://localhost:8000")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)