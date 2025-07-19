# python 3.10에 보안 문제 고려됨. 이후 다른 버전으로 변경 필요
FROM python:3.10-slim

WORKDIR /backend
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install debugpy

# 애플리케이션 코드 복사
COPY . .

ENV PYTHONPATH=/backend

# 이미지 업로드 디렉토리 생성
RUN mkdir -p uploads/interior uploads/processed

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

