FROM python:3.9-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Копирование файлов зависимостей
COPY pyproject.toml .

# Установка Poetry
RUN pip install poetry

# Конфигурация Poetry
RUN poetry config virtualenvs.create false

# Установка зависимостей
RUN poetry install --no-dev --no-interaction

# Установка PyTorch/torchvision совместимых с python:3.9-slim (CPU)
# Конкретные версии подбираются для стабильности fastai v1/DeOldify
RUN pip install --no-cache-dir torch==1.13.1 torchvision==0.14.1 --index-url https://download.pytorch.org/whl/cpu

# Установка fastai v1 и зависимостей DeOldify
RUN pip install --no-cache-dir fastai==1.0.61 fastprogress==1.0.3

# Установка DeOldify из GitHub (PyPI-пакета может не быть)
RUN pip install --no-cache-dir "git+https://github.com/jantic/DeOldify.git@master"

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