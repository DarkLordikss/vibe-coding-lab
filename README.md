# Система управления больницей

Веб-приложение для управления больницей, врачами, пациентами и диагнозами. Лабораторная работа по дисциплине "Базы данных" (модуль 4).

## Содержание

- [Стек технологий](#стек-технологий)
- [Архитектура](#архитектура)
- [Запуск](#запуск)
- [API Документация](#api-документация)
- [Тестирование](#тестирование)
- [Нагрузочное тестирование](#нагрузочное-тестирование)
- [Структура проекта](#структура-проекта)

## Стек технологий

- **Python 3.9+** - язык программирования
- **Tornado 6.0** - асинхронный веб-фреймворк
- **Redis 7** - хранилище данных (in-memory database)
- **Docker & Docker Compose** - контейнеризация
- **Locust** - инструмент для нагрузочного тестирования

## Архитектура

Проект следует принципам многослойной архитектуры с разделением ответственности:

### Слои приложения

```
┌─────────────────────────────────────┐
│         Presentation Layer          │
│         (handlers.py)               │
│  - HTTP Request Handlers            │
│  - Request Validation               │
│  - Response Formatting              │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│         Business Logic Layer        │
│         (main.py)                   │
│  - Application Setup                │
│  - Route Configuration              │
│  - Initialization Logic              │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│         Data Access Layer           │
│         (database.py)               │
│  - Database Abstraction             │
│  - Redis Operations                 │
│  - Key Management                   │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│         Storage Layer                │
│         (Redis)                      │
│  - In-Memory Data Storage            │
│  - Hash Tables & Sets               │
└─────────────────────────────────────┘
```

### Модули проекта

#### `main.py`
- Точка входа приложения
- Инициализация веб-сервера Tornado
- Настройка маршрутов
- Инициализация базы данных

#### `handlers.py`
- HTTP обработчики запросов
- Базовый класс `BaseHandler` с общей логикой обработки ошибок
- Специализированные обработчики для каждой сущности:
  - `MainHandler` - главная страница
  - `HospitalHandler` - управление больницами
  - `DoctorHandler` - управление врачами
  - `PatientHandler` - управление пациентами
  - `DiagnosisHandler` - управление диагнозами
  - `DoctorPatientHandler` - связи врач-пациент

#### `database.py`
- Абстракция для работы с Redis
- Класс `Database` - обертка над Redis операциями
- Класс `RedisKeys` - константы и утилиты для ключей Redis
- Управление auto-increment ID для всех сущностей

### Модель данных

#### Сущности

1. **Hospital** (Больница)
   - `name` - название
   - `address` - адрес
   - `beds_number` - количество коек
   - `phone` - телефон

2. **Doctor** (Врач)
   - `surname` - фамилия
   - `profession` - специальность
   - `hospital_ID` - ID больницы (опционально)

3. **Patient** (Пациент)
   - `surname` - фамилия
   - `born_date` - дата рождения (формат: YYYY-MM-DD)
   - `sex` - пол ('M' или 'F')
   - `mpn` - медицинский полис номер

4. **Diagnosis** (Диагноз)
   - `patient_ID` - ID пациента
   - `type` - тип диагноза
   - `information` - дополнительная информация

5. **Doctor-Patient Relationship** (Связь врач-пациент)
   - Многие-ко-многим через Redis Sets
   - Ключ: `doctor-patient:{doctor_ID}`

### Хранение данных в Redis

- **Hash Tables** для сущностей: `{entity}:{id}` → поля и значения
- **Strings** для счетчиков: `{entity}:autoID` → текущий ID
- **Sets** для связей: `doctor-patient:{doctor_ID}` → множество patient_ID

## Запуск

### Запуск с Docker (рекомендуется)

#### Требования
- Docker 20.10+
- Docker Compose 2.0+

#### Быстрый старт

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

#### Управление сервисами

```bash
# Пересобрать образы
docker-compose build

# Перезапустить приложение
docker-compose restart app

# Просмотр статуса
docker-compose ps
```

### Локальный запуск (без Docker)

#### Требования
- Python 3.9+
- Redis 7+
- pip

#### Установка

```bash
# Установить зависимости
pip install -r requirements.txt

# Запустить Redis (если не запущен)
# Linux/Mac:
redis-server

# Windows: используйте Redis из WSL или установите через Chocolatey
```

#### Настройка

При необходимости измените настройки подключения к Redis в `main.py` (строки 22-23) или используйте переменные окружения:

```bash
export REDIS_HOST=localhost
export REDIS_PORT=6379
```

#### Запуск приложения

```bash
python main.py
```

Приложение будет доступно по адресу: http://localhost:8888

## API Документация

Все API эндпоинты поддерживают два метода:
- **GET** - получение списка сущностей (возвращает HTML страницу)
- **POST** - создание новой сущности (принимает form-data)

### Базовый URL
```
http://localhost:8888
```

### Эндпоинты

#### 1. Главная страница

**GET** `/`

Возвращает главную страницу приложения.

**Пример запроса:**
```bash
curl http://localhost:8888/
```

---

#### 2. Больницы (Hospitals)

**GET** `/hospital`

Получить список всех больниц.

**Пример запроса:**
```bash
curl http://localhost:8888/hospital
```

**POST** `/hospital`

Создать новую больницу.

**Параметры:**
- `name` (обязательный) - название больницы
- `address` (обязательный) - адрес
- `beds_number` (опциональный) - количество коек
- `phone` (опциональный) - телефон

**Пример запроса:**
```bash
curl -X POST http://localhost:8888/hospital \
  -d "name=City Hospital" \
  -d "address=123 Main St" \
  -d "beds_number=200" \
  -d "phone=+1234567890"
```

**Успешный ответ:**
```
OK: ID 1 for City Hospital
```

**Ошибки:**
- `400` - "Hospital name and address required" (если не указаны обязательные поля)
- `400` - "Redis connection refused" (если Redis недоступен)
- `500` - "Something went terribly wrong" (ошибка сохранения)

---

#### 3. Врачи (Doctors)

**GET** `/doctor`

Получить список всех врачей.

**POST** `/doctor`

Создать нового врача.

**Параметры:**
- `surname` (обязательный) - фамилия врача
- `profession` (обязательный) - специальность
- `hospital_ID` (опциональный) - ID больницы

**Пример запроса:**
```bash
curl -X POST http://localhost:8888/doctor \
  -d "surname=Smith" \
  -d "profession=Surgeon" \
  -d "hospital_ID=1"
```

**Успешный ответ:**
```
OK: ID 1 for Smith
```

**Ошибки:**
- `400` - "Surname and profession required"
- `400` - "No hospital with such ID" (если указан несуществующий hospital_ID)
- `400` - "Redis connection refused"
- `500` - "Something went terribly wrong"

---

#### 4. Пациенты (Patients)

**GET** `/patient`

Получить список всех пациентов.

**POST** `/patient`

Создать нового пациента.

**Параметры:**
- `surname` (обязательный) - фамилия
- `born_date` (обязательный) - дата рождения (формат: YYYY-MM-DD)
- `sex` (обязательный) - пол ('M' или 'F')
- `mpn` (обязательный) - номер медицинского полиса

**Пример запроса:**
```bash
curl -X POST http://localhost:8888/patient \
  -d "surname=Doe" \
  -d "born_date=1990-01-15" \
  -d "sex=M" \
  -d "mpn=123456"
```

**Успешный ответ:**
```
OK: ID 1 for Doe
```

**Ошибки:**
- `400` - "All fields required"
- `400` - "Sex must be 'M' or 'F'"
- `400` - "Redis connection refused"
- `500` - "Something went terribly wrong"

---

#### 5. Диагнозы (Diagnoses)

**GET** `/diagnosis`

Получить список всех диагнозов.

**POST** `/diagnosis`

Создать новый диагноз.

**Параметры:**
- `patient_ID` (обязательный) - ID пациента
- `type` (обязательный) - тип диагноза
- `information` (опциональный) - дополнительная информация

**Пример запроса:**
```bash
curl -X POST http://localhost:8888/diagnosis \
  -d "patient_ID=1" \
  -d "type=Flu" \
  -d "information=Patient has flu symptoms"
```

**Успешный ответ:**
```
OK: ID 1 for patient Doe
```

**Ошибки:**
- `400` - "Patiend ID and diagnosis type required"
- `400` - "No patient with such ID"
- `400` - "Redis connection refused"
- `500` - "Something went terribly wrong"

---

#### 6. Связи врач-пациент (Doctor-Patient Relationships)

**GET** `/doctor-patient`

Получить все связи между врачами и пациентами.

**POST** `/doctor-patient`

Создать связь между врачом и пациентом.

**Параметры:**
- `doctor_ID` (обязательный) - ID врача
- `patient_ID` (обязательный) - ID пациента

**Пример запроса:**
```bash
curl -X POST http://localhost:8888/doctor-patient \
  -d "doctor_ID=1" \
  -d "patient_ID=1"
```

**Успешный ответ:**
```
OK: doctor ID: 1, patient ID: 1
```

**Ошибки:**
- `400` - "ID required"
- `400` - "No such ID for doctor or patient"
- `400` - "Redis connection refused"

---

### Коды ответов

- `200` - Успешный запрос
- `400` - Ошибка валидации или подключения к Redis
- `500` - Внутренняя ошибка сервера

## Тестирование

### Запуск тестов в Docker

```bash
# Запустить все тесты
docker-compose --profile testing run --rm tests

# Запустить с подробным выводом
docker-compose --profile testing run --rm tests python -m unittest test_main -v

# Запустить конкретный тест
docker-compose --profile testing run --rm tests python -m unittest test_main.TestHospitalHandler -v
```

### Локальный запуск тестов

```bash
# С использованием unittest
python -m unittest test_main

# Или напрямую
python test_main.py

# С подробным выводом
python -m unittest test_main -v
```

### Покрытие тестами

Тесты покрывают:
- ✅ Все HTTP обработчики (GET и POST)
- ✅ Валидацию входных данных
- ✅ Обработку ошибок Redis
- ✅ Проверку существования связанных сущностей
- ✅ Инициализацию базы данных

**Примечание:** Тесты используют мокирование Redis, поэтому для их запуска не требуется запущенный экземпляр Redis.

## Нагрузочное тестирование

Проект включает нагрузочные тесты на базе Locust.

### Запуск через Docker Compose

```bash
# Запустить нагрузочное тестирование
docker-compose --profile testing up load-test

# Веб-интерфейс будет доступен на http://localhost:8089
```

### Локальный запуск

```bash
# Установить Locust (если не установлен)
pip install locust

# Запустить тест
locust -f load_test.py --host=http://localhost:8888

# Или с параметрами
locust -f load_test.py --host=http://localhost:8888 --users=100 --spawn-rate=10

# Headless режим (без веб-интерфейса)
locust -f load_test.py --host=http://localhost:8888 --users=50 --spawn-rate=5 --run-time=5m --headless
```

### Веб-интерфейс Locust

После запуска откройте http://localhost:8089 для доступа к веб-интерфейсу, где можно:
- Управлять количеством пользователей
- Наблюдать статистику в реальном времени
- Экспортировать результаты

### Сценарии тестирования

Тест симулирует реалистичное поведение пользователей:
- Просмотр страниц (GET запросы) - 70% нагрузки
- Создание сущностей (POST запросы) - 30% нагрузки
- Создание связей между сущностями
- Обработка ошибок и валидации

## Структура проекта

```
vibe-coding-lab/
├── main.py                 # Точка входа, настройка приложения
├── handlers.py             # HTTP обработчики запросов
├── database.py             # Абстракция для работы с Redis
├── test_main.py            # Юнит-тесты
├── load_test.py            # Нагрузочные тесты (Locust)
├── requirements.txt        # Python зависимости
├── Dockerfile              # Образ для приложения
├── Dockerfile.test         # Образ для тестов
├── docker-compose.yml      # Конфигурация Docker Compose
├── README.md               # Документация (этот файл)
├── templates/              # HTML шаблоны
│   ├── index.html
│   ├── hospital.html
│   ├── doctor.html
│   ├── patient.html
│   ├── diagnosis.html
│   └── doctor-patient.html
└── static/                 # Статические файлы
    ├── css/
    └── js/
```

## Переменные окружения

| Переменная | Описание | Значение по умолчанию |
|-----------|----------|----------------------|
| `REDIS_HOST` | Хост Redis | `localhost` |
| `REDIS_PORT` | Порт Redis | `6379` |
| `TORNADO_AUTORELOAD` | Автоперезагрузка при изменении кода | `True` |
| `TORNADO_DEBUG` | Режим отладки | `True` |
| `TORNADO_SERVE_TRACEBACK` | Показывать traceback в ошибках | `True` |

## Разработка

### Добавление новых эндпоинтов

1. Создайте новый обработчик в `handlers.py`, наследуя от `BaseHandler`
2. Добавьте методы `get()` и/или `post()`
3. Используйте `get_database()` для работы с данными
4. Добавьте маршрут в `main.py` в функцию `make_app()`
5. Создайте HTML шаблон в `templates/` (если нужен GET запрос)

### Работа с базой данных

Используйте класс `Database` из `database.py`:

```python
from database import get_database

db = get_database()

# Получить все сущности
hospitals = db.get_all_entities("hospital")

# Получить одну сущность
hospital = db.get_entity("hospital", "1")

# Создать сущность
fields = {'name': 'Hospital', 'address': 'Address'}
db.create_entity("hospital", "1", fields)

# Получить/увеличить auto ID
current_id = db.get_auto_id("hospital")
db.increment_auto_id("hospital")
```

## Лицензия

Учебный проект для лабораторной работы.

## Контакты

Для вопросов и предложений создайте issue в репозитории проекта.
