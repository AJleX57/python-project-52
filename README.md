### Hexlet tests and linter status:
[![Actions Status](https://github.com/AJleX57/python-project-52/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/AJleX57/python-project-52/actions)
[![Quality gate](https://sonarcloud.io/api/project_badges/quality_gate?project=AJleX57_python-project-52)](https://sonarcloud.io/summary/new_code?id=AJleX57_python-project-52)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=AJleX57_python-project-52&metric=coverage)](https://sonarcloud.io/summary/new_code?id=AJleX57_python-project-52)

# Hexlet Task Manager

Task Manager — веб-приложение для управления задачами, разработанное на Django.

Приложение позволяет создавать задачи, назначать исполнителей, добавлять статусы и метки, а также отслеживать выполнение работы. Для доступа к основным возможностям необходимо зарегистрироваться и войти в систему.

## Возможности приложения

Пользователь может:

- зарегистрироваться, войти в систему и выйти из неё;
- просматривать список пользователей;
- изменять и удалять собственную учётную запись;
- создавать, изменять и удалять статусы;
- создавать, изменять и удалять метки;
- создавать задачи и добавлять к ним описание;
- назначать задаче статус и исполнителя;
- прикреплять к задаче несколько меток;
- просматривать подробную информацию о задаче;
- изменять созданные задачи;
- удалять только те задачи, автором которых он является;
- фильтровать задачи по статусу, исполнителю и метке;
- выводить только собственные задачи.

Приложение также защищает связанные данные. Нельзя удалить пользователя, статус или метку, если они используются в существующих задачах.

## Стек технологий

- Python 3.12
- Django 5.2
- PostgreSQL
- SQLite для локальной разработки
- Django Filter
- Bootstrap 5
- Gunicorn
- WhiteNoise
- Rollbar
- uv
- Ruff
- Coverage.py
- SonarQube Cloud
- GitHub Actions
- Render

## Развёрнутое приложение

Приложение доступно по ссылке:

[Открыть Hexlet Task Manager](https://hexlet-code-ajlex57.onrender.com/)

## Установка и запуск локально

### 1. Клонирование репозитория

```bash
git clone https://github.com/AJleX57/python-project-52.git
cd python-project-52
```

### 2. Установка uv

Если `uv` ещё не установлен:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

После установки перезапусти терминал.

### 3. Установка зависимостей

```bash
uv sync
```

### 4. Настройка переменных окружения

Создай файл `.env` на основе примера:

```bash
cp .env.example .env
```

Пример содержимого `.env`:

```dotenv
SECRET_KEY=замени-на-случайную-секретную-строку
DEBUG=True

SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
```

Без переменной `DATABASE_URL` приложение будет использовать локальную базу данных SQLite.

Для использования PostgreSQL добавь:

```dotenv
DATABASE_URL=postgresql://postgres:password@localhost:5432/task_manager
```

Где:

- `postgres` — имя пользователя PostgreSQL;
- `password` — пароль пользователя;
- `task_manager` — имя базы данных.

Создать базу данных можно командой:

```bash
createdb task_manager
```

### 5. Применение миграций

```bash
uv run python manage.py migrate
```

### 6. Запуск сервера разработки

```bash
uv run python manage.py runserver
```

После запуска приложение будет доступно по адресу:

```text
http://127.0.0.1:8000
```

## Запуск тестов

Для запуска тестов Django:

```bash
uv run python manage.py test
```

Для запуска тестов с измерением покрытия:

```bash
uv run coverage erase
uv run coverage run manage.py test
uv run coverage report -m
```

Для создания HTML-отчёта:

```bash
uv run coverage html
```

Отчёт будет находиться в файле:

```text
htmlcov/index.html
```

## Проверка качества кода

Проверка проекта с помощью Ruff:

```bash
uv run ruff check .
```

Проверка форматирования:

```bash
uv run ruff format --check .
```

Автоматическое форматирование:

```bash
uv run ruff format .
```

## Сбор статических файлов

```bash
uv run python manage.py collectstatic --noinput
```

Собранные файлы сохраняются в каталоге `staticfiles`.

## Запуск в продакшен-режиме

Перед запуском необходимо указать переменные окружения:

```dotenv
SECRET_KEY=секретный-ключ
DEBUG=False
DATABASE_URL=postgresql://user:password@host:5432/database

SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

Запуск приложения через Gunicorn:

```bash
uv run gunicorn task_manager.wsgi:application
```

## Мониторинг ошибок

Для отправки ошибок в Rollbar необходимо добавить переменные:

```dotenv
ROLLBAR_ACCESS_TOKEN=токен-проекта-rollbar
ROLLBAR_ENVIRONMENT=production
```

Если `ROLLBAR_ACCESS_TOKEN` не указан, интеграция с Rollbar будет отключена.

## Деплой

Приложение развёрнуто на платформе Render.

Во время сборки выполняются:

```bash
uv sync
uv run python manage.py migrate
uv run python manage.py collectstatic --noinput
```

Для запуска используется Gunicorn.

Ссылка на приложение:

[https://hexlet-code-ajlex57.onrender.com/](https://hexlet-code-ajlex57.onrender.com/)