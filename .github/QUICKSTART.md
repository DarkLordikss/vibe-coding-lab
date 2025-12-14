# Быстрый старт CI/CD

## Минимальная настройка для тестирования

### 1. Настройка Secrets (обязательно для деплоя)

Перейдите в **Settings → Secrets and variables → Actions** и добавьте:

```
SSH_PRIVATE_KEY    - ваш приватный SSH ключ
SSH_HOST           - IP или домен VM (например: 192.168.1.100)
SSH_USER           - пользователь SSH (например: ubuntu)
SSH_PORT           - порт SSH (опционально, по умолчанию 22)
```

### 2. Подготовка VM сервера

На VM сервере должны быть установлены:
- Docker
- Docker Compose
- curl (для health checks)

```bash
# Пример установки на Ubuntu
sudo apt-get update
sudo apt-get install -y docker.io docker-compose curl
sudo systemctl start docker
sudo systemctl enable docker
```

### 3. Настройка SSH доступа

```bash
# На вашей машине
ssh-keygen -t rsa -b 4096 -C "github-actions"
ssh-copy-id user@your-vm-ip

# Скопируйте приватный ключ в GitHub Secrets
cat ~/.ssh/id_rsa
```

### 4. Запуск Pipeline

Pipeline запустится автоматически при push в `main`/`master`/`develop` или можно запустить вручную:

1. Перейдите в **Actions** tab
2. Выберите **CI/CD Pipeline**
3. Нажмите **Run workflow**

## Что делает Pipeline

1. ✅ **Build** - Собирает Docker образ
2. ✅ **Unit Tests** - Запускает юнит-тесты
3. ✅ **Docker Tests** - Тесты в контейнере
4. ✅ **Load Tests** - Нагрузочное тестирование (10 пользователей, 30 секунд)
5. ✅ **Deploy** - Развертывание на VM
6. ✅ **Rollback** - Автоматический откат при ошибке деплоя

**Важно:** Весь pipeline работает **только** для веток `main` и `master`.

## Проверка работы

После деплоя проверьте:

```bash
# На VM сервере
docker ps
curl http://localhost:8888/
curl http://localhost:8888/analytics
```

## Troubleshooting

### Pipeline не запускается
- Проверьте, что файл `.github/workflows/ci-cd.yml` существует
- Убедитесь, что вы в правильной ветке

### Тесты падают
- Проверьте логи в Actions tab
- Убедитесь, что все зависимости в `requirements.txt`

### Деплой не работает
- Проверьте SSH подключение вручную
- Убедитесь, что все secrets настроены
- Проверьте логи в шаге "Deploy to VM"

### Приложение не отвечает после деплоя
- Проверьте логи: `docker-compose logs`
- Убедитесь, что порт 8888 открыт
- Проверьте, что Redis запущен

## Отключение деплоя

Если нужно отключить автоматический деплой, закомментируйте job `deploy` в `.github/workflows/ci-cd.yml`:

```yaml
# deploy:
#   name: Deploy to VM (Mock)
#   ...
```

