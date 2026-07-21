SHELL := /bin/bash

# Позволяет запускать python и gunicorn напрямую из .venv.
export PATH := $(CURDIR)/.venv/bin:$(PATH)

.PHONY: install migrate collectstatic build render-start dev check


install:
	uv sync --frozen


migrate:
	python manage.py migrate


collectstatic:
	python manage.py collectstatic --noinput


build:
	./build.sh


render-start:
	gunicorn task_manager.wsgi:application --bind 0.0.0.0:$${PORT:-8000}


dev:
	python manage.py runserver


check:
	python manage.py check

.PHONY: test


test:
	python manage.py test

test-coverage:
	coverage erase
	coverage run manage.py test
	coverage report
	coverage xml

lint:
	uv run ruff check .


format-check:
	uv run ruff format --check .


format:
	uv run ruff format .