# app/main.py
from fastapi import FastAPI
from app.user.interface.controller import user_controller
from app.interior.interface.controller import interior_controller
from prometheus_fastapi_instrumentator import Instrumentator


app = FastAPI()


# 라우터 등록
app.include_router(user_controller.router)
app.include_router(interior_controller.router)
# 👉 Prometheus metrics 등록
Instrumentator().instrument(app).expose(app)
