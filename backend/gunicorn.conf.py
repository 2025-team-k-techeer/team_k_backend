import multiprocessing
import os

# 서버 소켓
bind = "0.0.0.0:8000"
backlog = 2048

# 워커 프로세스
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
preload_app = True

# 타임아웃 설정
timeout = 120
keepalive = 2

# 로깅 설정
accesslog = "-"  # stdout으로 출력
errorlog = "-"  # stderr로 출력
loglevel = os.getenv("LOG_LEVEL", "info").lower()
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# 프로세스 이름
proc_name = "team_k_backend"

# 데몬 모드 (False로 설정하여 포그라운드에서 실행)
daemon = False

# 사용자/그룹 (Docker 환경에서는 필요 없음)
# user = "www-data"
# group = "www-data"

# 임시 디렉토리
tmp_upload_dir = None

# 보안 설정
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# 환경 변수
raw_env = [
    "PYTHONPATH=/backend",
]
