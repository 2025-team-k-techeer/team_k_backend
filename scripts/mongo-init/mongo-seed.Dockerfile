FROM google/cloud-sdk:alpine

# MongoDB 클라이언트 설치
RUN apk add --no-cache mongodb-tools