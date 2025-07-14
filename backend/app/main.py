# backend/app/main.py

from fastapi import FastAPI
import redis
from pymongo import MongoClient
import httpx

app = FastAPI()


@app.get("/test/redis")
def test_redis():
    try:
        r = redis.Redis(host="redis", port=6379)
        r.set("test_key", "test_value")
        value = r.get("test_key")
        return {"redis_alive": True, "value": value.decode()}
    except Exception as e:
        return {"redis_alive": False, "error": str(e)}


@app.get("/test/mongo")
def test_mongo():
    try:
        client = MongoClient("mongodb://admin:admin123@mongo:27017")
        db = client.test_db
        result = db.test_col.insert_one({"name": "sample", "value": 123})
        return {"mongo_alive": True, "inserted_id": str(result.inserted_id)}
    except Exception as e:
        return {"mongo_alive": False, "error": str(e)}


@app.get("/test/qdrant")
def test_qdrant():
    try:
        response = httpx.get("http://qdrant:6333/collections")
        return {"qdrant_alive": response.status_code == 200, "data": response.json()}
    except Exception as e:
        return {"qdrant_alive": False, "error": str(e)}
