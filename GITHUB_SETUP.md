# Как отправить проект на GitHub

## 1. Создайте репозиторий на GitHub

1. Зайдите на [github.com](https://github.com) и войдите в аккаунт.
2. Нажмите **"+"** в правом верхнем углу → **"New repository"**.
3. Укажите имя репозитория (например, `ai-integration-tool`).
4. Выберите **Public** или **Private**.
5. **Не** ставьте галочки "Add a README" и "Add .gitignore" — проект уже есть локально.
6. Нажмите **"Create repository"**.

## 2. Инициализируйте Git и отправьте код

В терминале в папке проекта выполните:

```powershell
# Перейти в папку проекта (если ещё не там)
cd "c:\Users\mradd\ai-integration-tool"

# Инициализировать репозиторий
git init

# Добавить все файлы (config.yaml не попадёт — он в .gitignore)
git add .

# Первый коммит
git commit -m "Initial commit"

# Добавить удалённый репозиторий (замените YOUR_USERNAME и REPO_NAME на свои)
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git

# Отправить код на GitHub (ветка main)
git branch -M main
git push -u origin main
```

## 3. Если репозиторий уже создан на GitHub

Скопируйте URL репозитория со страницы репозитория (кнопка **"Code"** → HTTPS) и подставьте в команду:

```powershell
git remote add origin https://github.com/YOUR_USERNAME/ai-integration-tool.git
```

При первом `git push` GitHub может запросить логин и пароль. Используйте **Personal Access Token** вместо пароля (Settings → Developer settings → Personal access tokens).

---

**Важно:** Файл `config.yaml` с API-ключами в `.gitignore` и не попадёт в репозиторий — так и должно быть для безопасности.
