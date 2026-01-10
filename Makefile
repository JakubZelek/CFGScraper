.PHONY: rebuild

rebuild:
	docker compose down -v --rmi all
	docker compose build --no-cache url-api cfg-processor-cpp cfg-processor-python elasticsearch-upload
	docker compose up -d
