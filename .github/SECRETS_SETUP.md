# Настройка Secrets для CI/CD

## Необходимые Secrets

Для работы CI/CD pipeline необходимо настроить следующие secrets в GitHub репозитории:

### 1. SSH_PRIVATE_KEY
Приватный SSH ключ для доступа к VM серверу.

**Как получить:**
```bash
# На локальной машине или на сервере
ssh-keygen -t rsa -b 4096 -C "github-actions"
# Сохранить приватный ключ (id_rsa)
cat ~/.ssh/id_rsa
```

**Важно:** Добавьте публичный ключ на VM:
```bash
# На VM сервере
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

### 2. SSH_HOST
IP адрес или доменное имя VM сервера.

**Примеры:**
- `192.168.1.100`
- `deploy.example.com`
- `vm.production.local`

### 3. SSH_USER
Имя пользователя для SSH подключения.

**Примеры:**
- `ubuntu`
- `deploy`
- `admin`

### 4. SSH_PORT (опционально)
Порт SSH подключения. По умолчанию используется 22.

**Примеры:**
- `22` (стандартный)
- `2222` (кастомный порт)

## Инструкция по добавлению Secrets

1. Перейдите в ваш GitHub репозиторий
2. Нажмите на **Settings** (Настройки)
3. В левом меню выберите **Secrets and variables** → **Actions**
4. Нажмите **New repository secret**
5. Введите имя secret (например, `SSH_PRIVATE_KEY`)
6. Вставьте значение secret
7. Нажмите **Add secret**
8. Повторите для всех необходимых secrets

## Проверка настройки

После добавления всех secrets, создайте тестовый commit:

```bash
git commit --allow-empty -m "Test CI/CD pipeline"
git push
```

Проверьте выполнение workflow в разделе **Actions** вашего репозитория.

## Безопасность

⚠️ **Важные рекомендации:**

1. **Никогда не коммитьте secrets в код!**
2. Используйте разные SSH ключи для разных окружений
3. Регулярно ротируйте SSH ключи
4. Ограничьте доступ к secrets только необходимым пользователям
5. Используйте минимальные необходимые права для SSH пользователя

## Troubleshooting

### Ошибка "Permission denied (publickey)"
- Проверьте, что публичный ключ добавлен в `~/.ssh/authorized_keys` на VM
- Убедитесь, что права на файлы правильные: `chmod 600 ~/.ssh/authorized_keys`

### Ошибка "Connection refused"
- Проверьте, что SSH сервис запущен на VM
- Проверьте настройки firewall
- Убедитесь, что порт SSH открыт

### Ошибка "Host key verification failed"
- Добавьте VM в known_hosts или используйте `StrictHostKeyChecking=no` (не рекомендуется для production)

