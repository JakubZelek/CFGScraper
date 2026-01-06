.PHONY: rebuild

rebuild:
	docker compose down -v --rmi all
	docker compose build --no-cache url-api cfg-processor
	docker compose up -d
