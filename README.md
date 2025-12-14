# Python3 Application

Лаба дисциплины "Базы данных" (модуль 4)

## Стек технологий

- Python 3 (фреймворк tornado)

- Redis в качестве хранилки

## Запуск с Docker (рекомендуется)

### Требования
- Docker
- Docker Compose

### Запуск приложения

```bash
# Запустить все сервисы (Redis + приложение)
docker-compose up -d

# Просмотр логов
docker-compose logs -f app

# Остановка сервисов
docker-compose down

# Остановка с удалением данных Redis
docker-compose down -v
```

### Запуск тестов

```bash
# Запустить тесты
docker-compose --profile testing run --rm tests

# Или с подробным выводом
docker-compose --profile testing run --rm tests python -m unittest test_main -v
```

### Сборка образов

```bash
# Собрать все образы
docker-compose build

# Собрать только образ приложения
docker-compose build app

# Собрать только образ тестов
docker-compose build tests
```

## Локальный запуск (без Docker)

*примеры команд ниже указаны для unix-подобных ОС, с виндой разбирайтесь сами*

1. Ставим Redis, настраиваем и проверяем его работоспособность

2. Устанавливаем Python 3 и пакетный менеджер pip для своей ОС (hard way)

3. ... или ставим IDE PyCharm, которая упростит эту задачу (easy way)

4. При необходимости, меняем адрес сервера Redis в 12 строке файл `main.py`

5. Ставим необходимые зависимости командой ` $ pip3 install -r requirements.txt`

6. Запускаем веб-сервис командой ` $ python3 main.py`

## Дополнительно

Сервис доступен по адресу http://localhost:8888

## Запуск тестов

Для запуска юнит-тестов используйте одну из следующих команд:

```bash
# С использованием unittest (встроенный в Python)
python -m unittest test_main

# Или напрямую
python test_main.py

# С использованием pytest (если установлен)
pytest test_main.py -v
```

Тесты используют мокирование Redis, поэтому для их запуска не требуется запущенный экземпляр Redis.
