# Docker Dev 명령어 (FastAPI 개발환경)

docker-dev-up:
	docker compose -f dev-docker-compose.yml up --build -d

docker-dev-down:
	docker compose -f dev-docker-compose.yml down

docker-dev-logs:
	docker compose -f dev-docker-compose.yml logs -f

docker-dev-logs-fastapi:
	docker compose -f dev-docker-compose.yml logs -f fastapi

docker-dev-logs-recent:
	docker compose -f dev-docker-compose.yml logs --tail=100

# 로그 뷰어 스크립트 사용
logs-follow:
	python scripts/log_viewer.py --follow --service fastapi

logs-recent:
	python scripts/log_viewer.py --service fastapi --lines 50

docker-dev-sh:
	docker exec -it fastapi bash

docker-dev-mongo-sh:
	docker exec -it mongo bash
	
docker-dev-down-v:
	docker compose -f dev-docker-compose.yml down -v

docker-deploy-up:
	docker compose -f deploy-docker-compose.yml up --build -d

docker-deploy-down:
	docker compose -f deploy-docker-compose.yml down

docker-deploy-logs:
	docker compose -f deploy-docker-compose.yml logs -f

docker-deploy-down-v:
	docker compose -f deploy-docker-compose.yml down -v

