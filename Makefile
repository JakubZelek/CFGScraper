.PHONY: rebuild build list-topics

rebuild:
	docker compose down -v --rmi all
	docker compose build
	docker compose up -d

build:
	docker compose build
	docker compose up -d

