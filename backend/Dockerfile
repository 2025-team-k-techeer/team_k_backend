# python 3.10에 보안 문제 고려됨. 이후 다른 버전으로 변경 필요
FROM python:3.10-slim

WORKDIR /backend
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install debugpy

ENV PYTHONPATH=/backend

