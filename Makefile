.PHONY: up down build migrate import logs shell

up:
	docker compose up -d

down:
	docker compose down

build:
	docker compose build

migrate:
	docker compose exec backend python manage.py migrate

import:
	docker compose exec backend python manage.py import_questions --file questions.json

collectstatic:
	docker compose exec backend python manage.py collectstatic --noinput

superuser:
	docker compose exec backend python manage.py createsuperuser

logs:
	docker compose logs -f

shell:
	docker compose exec backend python manage.py shell

db-shell:
	docker compose exec db psql -U pdd -d pdd

restart:
	docker compose restart

# First-time setup on server
setup: build up migrate import collectstatic
	@echo "Setup complete!"
