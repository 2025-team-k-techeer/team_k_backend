# app/main.py
from fastapi import FastAPI
from app.user.interface.controller import user_controller
from app.interior.interface.controller import interior_controller
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi.middleware.cors import CORSMiddleware
from app.utils.logger import setup_logger
from app.config import get_settings

# 로깅 설정
settings = get_settings()
logger = setup_logger("team_k_backend", settings.LOG_LEVEL, log_file=settings.LOG_FILE)
logger.info("🚀 FastAPI 애플리케이션 시작")

app = FastAPI()


# 허용할 origin 리스트
origins = [
    "https://zipkku.shop",  # 프론트엔드 도메인
    "http://localhost:5173",  # ✅ Vite 기본 포트
    "https://localhost:5173",  # ✅ Vite 기본 포트
    # "*",  # 모든 origin 허용 (개발용)
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # "*"을 넣으면 모든 origin 허용 (개발용)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "X-Requested-With",
        "Accept",
        "Origin",
        "Referer",
    ],
)


# 라우터 등록
app.include_router(user_controller.router)
app.include_router(interior_controller.router)
# 👉 Prometheus metrics 등록
Instrumentator().instrument(app).expose(app)

from app.interior.interface.controller.ar_controller import router as ar_router

app.include_router(ar_router)
