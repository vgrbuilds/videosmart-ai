# VideoSmart AI 🎥🤖

VideoSmart AI is a state-of-the-art AI-powered SaaS application that takes video input (YouTube links or direct file uploads), transcribes them, generates structured meeting summaries/action items, and provides a RAG-based interactive chat interface for users to query details about the video.

## Features

- **Secure Authentication & Profile Management**: Complete user register/login flow using JWT tokens and secure password hashing.
- **YouTube Link Support**: Download and extract audio directly from any YouTube video URL with automatic bot-bypass.
- **Direct Video Uploads**: Securely upload local meeting video/audio files to Cloudinary for media management and processing.
- **AI Cloud Transcription (100% Serverless)**: Utilizes Google Gemini's File API to transcribe audio chunks without requiring heavy local machine STT libraries.
- **Interactive AI Chat Assistant (RAG)**: Chat with your videos using a MongoDB Atlas Vector Search indexing system.
- **Optimized Latency**: Skip rephrasing for standalone follow-up queries and utilize history truncation for faster responses.

---

## Repository Structure

```
videosmart-ai/
├── client/                 # React frontend application (Vite, Ant Design, TailwindCSS)
├── server/                 # FastAPI REST API (Python, Pydantic, MongoDB, LangChain)
├── docker-compose.yml      # Root configuration for containerized deployment
```

---

## Prerequisites

Ensure you have the following installed on your host system:
1. **Node.js** (v18+) - Required for client and signature generation.
2. **Python** (v3.12+) - Required for the backend server.
3. **MongoDB** - Database for user profiles, chat history, and vector storage.
4. **Git**

---

## Getting Started (Local Setup)

### 1. Backend Server Setup

Navigate to the `server/` directory and configure the environment:
```bash
cd server
```

Create a `.env` file with the following variables:
```env
MONGO_URI=mongodb+srv://<username>:<password>@cluster.mongodb.net/database
DATABASE_NAME=videosmart

# Gemini Configuration
GEMINI_API_KEY=your_google_gemini_api_key
GEMINI_MODEL_NAME=gemini-3.1-flash-lite

# Cloudinary Configuration
CLOUDINARY_CLOUD_NAME=your_cloudinary_cloud_name
CLOUDINARY_API_KEY=your_cloudinary_api_key
CLOUDINARY_API_SECRET=your_cloudinary_api_secret

# Other Configuration
CLIENT_URL=http://localhost:5173
PORT=8000
JWT_SECRET_KEY=your_super_secret_jwt_signature_key_that_is_long_enough
JWT_ALGORITHM=HS256
```

Sync package dependencies and start the backend:
```bash
uv sync
uv run python main.py
```
The server will start at `http://localhost:8000`. You can access the API Swagger docs at `http://localhost:8000/docs`.

### 2. Frontend Client Setup

Navigate to the `client/` directory and configure the environment:
```bash
cd ../client
```

Create a `.env` file:
```env
VITE_API_URL=http://localhost:8000
```

Install packages and run the development server:
```bash
npm install
npm run dev
```
The React client will launch at `http://localhost:5173`.

---

## Running Containerized (Docker Compose)

To launch the entire stack using Docker Compose:
1. Ensure your backend environment values are set in `server/.env`.
2. Run the build and launch command from the root directory:
   ```bash
   docker compose up --build -d
   ```
3. Open:
   - **Frontend App**: `http://localhost` (port 80)
   - **Backend API Docs**: `http://localhost:8000/docs`

---

## MongoDB Atlas Search Configuration

To enable vector search queries, configure a Vector Search Index named `vector_index` on the `video_chunks` collection:
```json
{
  "fields": [
    {
      "numDimensions": 3072,
      "path": "embedding",
      "similarity": "cosine",
      "type": "vector"
    },
    {
      "path": "video_id",
      "type": "filter"
    }
  ]
}
```
