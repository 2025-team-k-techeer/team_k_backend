FROM python:3.10-slim

# 필요한 패키지 설치
RUN pip install --no-cache-dir google-cloud-storage requests

# 업로드 스크립트 복사
# 경로 수정: scripts/qdrant-init/upload_qdrant.py → /upload_qdrant.py
COPY scripts/qdrant-init/upload_qdrant.py /upload_qdrant.py

# (선택) 타임존, 로케일 등 추가 설정 가능

# 기본 실행 명령
CMD ["python", "/upload_qdrant.py"]