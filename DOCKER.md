# Инструкция по использованию Docker

## Быстрый старт

### 1. Запуск приложения

```bash
# Запустить Redis и приложение
docker-compose up -d

# Приложение будет доступно по адресу http://localhost:8888
# Redis будет доступен на localhost:6379
```

### 2. Просмотр логов

```bash
# Логи приложения
docker-compose logs -f app

# Логи Redis
docker-compose logs -f redis

# Все логи
docker-compose logs -f
```

### 3. Запуск тестов

```bash
# Запустить все тесты
docker-compose --profile testing run --rm tests

# Запустить тесты с подробным выводом
docker-compose --profile testing run --rm tests python -m unittest test_main -v

# Запустить конкретный тест
docker-compose --profile testing run --rm tests python -m unittest test_main.TestHospitalHandler.test_post_success -v
```

### 4. Остановка сервисов

```bash
# Остановить все сервисы
docker-compose down

# Остановить и удалить данные Redis
docker-compose down -v
```

## Полезные команды

### Пересборка образов

```bash
# Пересобрать все образы
docker-compose build --no-cache

# Пересобрать только приложение
docker-compose build --no-cache app

# Пересобрать только тесты
docker-compose build --no-cache tests
```

### Выполнение команд в контейнере

```bash
# Войти в контейнер приложения
docker-compose exec app bash

# Выполнить команду в контейнере приложения
docker-compose exec app python -c "import redis; print('Redis OK')"

# Войти в контейнер Redis
docker-compose exec redis sh
```

### Просмотр статуса

```bash
# Статус всех сервисов
docker-compose ps

# Использование ресурсов
docker stats
```

## Структура сервисов

- **redis**: Сервер Redis (порт 6379)
- **app**: Tornado веб-приложение (порт 8888)
- **tests**: Контейнер для запуска тестов (запускается только с профилем `testing`)

## Переменные окружения

Все переменные окружения можно настроить в `docker-compose.yml`:

- `REDIS_HOST`: Хост Redis (по умолчанию: `redis`)
- `REDIS_PORT`: Порт Redis (по умолчанию: `6379`)
- `TORNADO_AUTORELOAD`: Автоперезагрузка при изменении кода (по умолчанию: `false`)
- `TORNADO_DEBUG`: Режим отладки (по умолчанию: `false`)

## Устранение проблем

### Проблема: Порт уже занят

Если порт 8888 или 6379 уже занят, измените порты в `docker-compose.yml`:

```yaml
ports:
  - "8889:8888"  # Вместо 8888:8888
```

### Проблема: Контейнер не запускается

```bash
# Проверить логи
docker-compose logs app

# Пересобрать образ
docker-compose build --no-cache app
docker-compose up -d
```

### Проблема: Redis недоступен

```bash
# Проверить здоровье Redis
docker-compose exec redis redis-cli ping

# Должен вернуть: PONG
```

