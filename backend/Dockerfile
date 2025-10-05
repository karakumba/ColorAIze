FROM python:3.9-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Копирование файлов зависимостей
COPY pyproject.toml .

# Установка Poetry
RUN pip install poetry

# Конфигурация Poetry
RUN poetry config virtualenvs.create false

# Установка зависимостей
RUN poetry install --no-dev --no-interaction

# Копирование исходного кода
COPY app/ ./app/
COPY download_model.py .

# Создание необходимых директорий
RUN mkdir -p storage/uploads storage/processed models

# Скачивание модели (опционально, можно вынести в отдельный сервис)
RUN python download_model.py || echo "Model download failed, will use mock mode"

# Открытие порта
EXPOSE 8000

# Запуск приложения
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]