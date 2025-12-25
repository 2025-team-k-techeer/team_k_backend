# 🏠 Zipkku Backend
Zipkku는 사용자가 원하는 인테리어 공간을 생성형 AI와 AR 기술로 구현할 수 있도록 지원하는 플랫폼입니다. 본 저장소는 Zipkku의 백엔드 시스템을 구성합니다.

## 📦 기술 스택 
![](diagram.png)

### 🧩 API
FastAPI – 비동기 Python 웹 프레임워크

Uvicorn – ASGI 서버

### 🗃️ 데이터베이스
MongoDB – 문서 기반 NoSQL 데이터베이스

Qdrant – 벡터 기반 유사도 검색 엔진

### ⚙️ 캐싱 및 비동기 작업 처리
Redis – 인메모리 캐시 및 브로커

Celery – 비동기 작업 큐

RabbitMQ – 메시지 브로커 (Celery 백엔드)

### 📊 모니터링 & 로깅
Loki + Promtail – 로그 수집 및 집계

Grafana – 시각화 대시보드

Prometheus – 메트릭 수집 및 알림

### 🔗 기타 인프라 요소
Docker – 모든 서비스는 컨테이너화 되어 관리됩니다.

Traefik – 리버스 프록시 및 로드 밸런싱

Google Cloud Run / Compute Engine – 배포 및 실행 환경

Google Cloud Storage – 정적 파일 저장

GitHub, GitLab, Vercel – CI/CD 및 프론트엔드 배포

## 프로젝트 구조

```
team_k_backend/
├── backend/
│   └── app/
│       ├── common/                  # 공통 유틸 및 설정
│       ├── integrations/           # 외부 API 및 서비스 연동
│       ├── interior/               # 인테리어 도메인 로직
│       │   ├── application/        # 서비스 로직
│       │   ├── domain/             # 도메인 모델
│       │   │   └── repository/     # 추상화된 저장소 인터페이스
│       │   ├── infra/              # 인프라 구현체
│       │   │   └── repository/     # 실제 저장소 구현
│       │   ├── interface/          # 입출력 계층 (Controller)
│       │   │   └── controller/
│       │   ├── schemas/            # Pydantic 스키마
│       │   └── tasks/              # 비동기 작업 (Celery 등)
│       ├── user/                   # 사용자 도메인 로직
│       │   ├── application/
│       │   ├── domain/
│       │   │   └── repository/
│       │   ├── infra/
│       │   │   ├── db_models/      # ORM 모델 정의
│       │   │   └── repository/
│       │   ├── interface/
│       │   │   └── controller/
│       │   └── schemas/
│       └── utils/                  # 보조 유틸리티 함수 모음
├── data/
│   └── qdrant/
│       └── data/
│           └── collections/        # Qdrant 벡터 데이터 저장소
├── key/                            # 인증 키 저장 위치
├── prometheus/                     # Prometheus 설정
├── promtail/                       # Promtail 설정
└── scripts/                        # 초기화 스크립트
    ├── mongo-init/
    └── qdrant-init/
```


