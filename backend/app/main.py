# main.py
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    print("hello")
    return {"message": "Hello World"}
