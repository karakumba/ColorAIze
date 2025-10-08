# ColorAIze - Image Colorization Project

AI-powered black and white image colorization system.

## Project Structure
```
ColorAIze/
├── backend/                    # FastAPI бэкенд
│   ├── app/                   # Основной Python пакет с логикой приложения
│   │   ├── __init__.py        # Инициализация Python пакета
│   │   ├── main.py            # FastAPI приложение и эндпоинты
│   │   └── colorizer.py       # Логика колоризации изображений
│   ├── tests/                 # Хранилище файлов
│   │   ├── test_api.py        
│   │   └── test_colorizer.py  
│   ├── storage/               # Хранилище файлов
│   │   ├── uploads/           # Временные загруженные файлы
│   │   └── processed/         # Обработанные цветные изображения
│   ├── pyproject.toml         # Зависимости Poetry для бэкенда
│   └── download_model.py      # Скрипт загрузки моделей ML
├── frontend/                   # React фронтенд
│   ├── public/                # Статические файлы
│   │   └── index.html         # Основной HTML шаблон
│   ├── src/                   # Исходный код React приложения
│   │   ├── App.jsx            # Главный React компонент
│   │   ├── App.css            # Стили приложения
│   │   └── main.jsx           # Точка входа React приложения
│   └── package.json           # Зависимости npm и скрипты
├── ml/                         # ML модели и обучение
│   ├── models/                # Веса предобученных моделей
│   ├── scripts/               # Python скрипты для работы с ML
│   │   ├── download_model.py  # Загрузка моделей DeOldify
│   │   ├── train.py           # Обучение моделей
│   │   └── evaluate.py        # Оценка качества моделей
│   ├── notebooks/             # Jupyter ноутбуки для экспериментов
│   │   └── experiments.ipynb  # Ноутбук для исследований и тестов
│   ├── data/                  # Датасеты для обучения
│   │   ├── raw/               # Исходные данные
│   │   └── processed/         # Обработанные данные
│   └── pyproject.toml         # Зависимости Poetry для ML части
└── README.md                  # Документация проекта
```

## 🚀 Инструкции по запуску

### Backend:
```bash
cd backend
poetry install
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
### Frontend:
```bash
cd frontend
npm install
npm run dev
```
### ML:
```bash
cd ml
poetry install
poetry run python scripts/download_model.py
```


## Запуск через docker

### Основные команды запуска:
```
# 1. Запуск всех сервисов (бэкенд + фронтенд)
docker-compose up -d

# 2. Запуск с загрузкой моделей ML
docker-compose --profile download up -d

# 3. Запуск только бэкенда
docker-compose up backend -d

# 4. Запуск только фронтенда
docker-compose up frontend -d

# 5. Запуск с пересборкой образов
docker-compose up -d --build

# 6. Запуск в режиме разработки (с логами)
docker-compose up
```
### Команды управления:
```
# 7. Остановка всех сервисов
docker-compose down

# 8. Остановка с удалением данных
docker-compose down -v

# 9. Просмотр логов всех сервисов
docker-compose logs -f

# 10. Просмотр логов конкретного сервиса
docker-compose logs -f backend
docker-compose logs -f frontend

# 11. Просмотр статуса контейнеров
docker-compose ps

# 12. Перезапуск конкретного сервиса
docker-compose restart backend
docker-compose restart frontend
```
### Команды для разработки:
```
# 13. Полная пересборка образов
docker-compose build --no-cache

# 14. Обновление конкретного сервиса
docker-compose up -d --build backend

# 15. Выполнение команд внутри контейнера
docker-compose exec backend bash
docker-compose exec frontend sh

# 16. Остановка и удаление всех образов
docker-compose down --rmi all

# 17. Очистка системы Docker
docker system prune -a
```
### Проверка работы:
```
# 18. Проверка здоровья бэкенда
curl http://localhost:8000/api/health

# 19. Проверка доступности фронтенда
curl -I http://localhost:3000
```

### После запуска приложение будет доступно:
Frontend: http://localhost:3000

Backend API: http://localhost:8000

API Documentation: http://localhost:8000/docs
