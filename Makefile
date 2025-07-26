# Docker Dev 명령어 (FastAPI 개발환경)

docker-dev-up:
	docker compose -f dev-docker-compose.yml up --build -d

docker-dev-down:
	docker compose -f dev-docker-compose.yml down

docker-dev-logs:
	docker compose -f dev-docker-compose.yml logs -f

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

