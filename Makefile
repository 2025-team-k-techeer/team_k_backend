# Docker Dev 명령어 (FastAPI 개발환경)

docker-dev-up:
	docker compose -f dev-docker-compose.yml up --build -d

docker-dev-down:
	docker compose -f dev-docker-compose.yml down

docker-dev-logs:
	docker compose -f dev-docker-compose.yml logs -f

docker-dev-sh:
	docker exec -it fastapi bash

