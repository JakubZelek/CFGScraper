.PHONY: rebuild

rebuild:
	docker compose down -v --rmi all
	docker build --no-cache -t url-app -f Dockerfile.UrlApp .
	docker compose up -d
