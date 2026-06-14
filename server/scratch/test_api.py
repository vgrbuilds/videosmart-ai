import sys, os
from unittest.mock import AsyncMock, MagicMock, patch

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fastapi.testclient import TestClient
from bson import ObjectId

mock_db = MagicMock()
mock_db.__getitem__.side_effect = lambda name: MagicMock()

with patch("app.db.mongodb.connect_to_mongo", new_callable=AsyncMock), \
     patch("app.db.mongodb.close_mongo_connection", new_callable=AsyncMock), \
     patch("app.db.mongodb.db_instance") as mock_db_instance:
    mock_db_instance.db = mock_db
    from app.main import app

client = TestClient(app)

def test_all():
    print("Testing Root...")
    r = client.get("/")
    assert r.status_code == 200 and r.json()["status"] == "online"
    
    print("Testing OpenAPI...")
    r = client.get("/api/openapi.json")
    assert r.status_code == 200 and "/api/auth/register" in r.json()["paths"]
    
    print("Testing Validation...")
    r = client.post("/api/auth/register", json={"username": "u", "email": "bad", "password": "123"})
    assert r.status_code == 422
    
    print("Testing Register...")
    with patch("app.services.auth_login.get_users_collection") as mock_get:
        mock_coll = MagicMock()
        mock_coll.find_one = AsyncMock(return_value=None)
        mock_coll.insert_one = AsyncMock(return_value=MagicMock(inserted_id=ObjectId()))
        mock_get.return_value = mock_coll
        r = client.post("/api/auth/register", json={"username": "alex", "email": "a@ex.com", "password": "password"})
        assert r.status_code == 201
        assert r.json()["username"] == "alex"

if __name__ == "__main__":
    try:
        test_all()
        print("\nSUCCESS: ALL TESTS PASSED!")
    except AssertionError as e:
        print(f"\n[FAIL] Assertion failed: {e}")
        sys.exit(1)
