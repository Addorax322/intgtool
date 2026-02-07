# Установка и запуск AI Integration Tool

Инструкция по скачиванию проекта с GitHub и запуску на устройстве.

**Требования:** Python 3.9+, Git

---

## Windows

### 1. Установка Python и Git

- **Python:** [python.org/downloads](https://www.python.org/downloads/) — при установке отметьте **Add Python to PATH**
- **Git:** [git-scm.com/download/win](https://git-scm.com/download/win)

### 2. Скачать проект

Откройте PowerShell или CMD и выполните:

```powershell
git clone https://github.com/Addorax322/intgtool.git
cd intgtool
```

### 3. Создать виртуальное окружение

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### 4. Установить зависимости

```powershell
pip install -r requirements.txt
```

### 5. Настроить конфиг и API-ключ

```powershell
copy config.example.yaml config.yaml
```

Задайте переменную окружения с API-ключом OpenRouter (получить ключ: [openrouter.ai/settings/keys](https://openrouter.ai/settings/keys)):

```powershell
$env:OPENROUTER_API_KEY = "ваш_ключ_здесь"
```

Или укажите ключ в `config.yaml` в секции `providers.openrouter.api_key`.

### 6. Запуск

```powershell
python main.py "Привет, объясни квантовые компьютеры"
```

Или с файлом:

```powershell
python main.py --input request.txt --output result.txt
```

---

## macOS

### 1. Установка Python и Git

Python 3 обычно уже установлен. Проверка:

```bash
python3 --version
git --version
```

Если нет — установите через Homebrew:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install python git
```

### 2. Скачать проект

```bash
git clone https://github.com/Addorax322/intgtool.git
cd intgtool
```

### 3. Создать виртуальное окружение

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Установить зависимости

```bash
pip install -r requirements.txt
```

### 5. Настроить конфиг и API-ключ

```bash
cp config.example.yaml config.yaml
```

Задайте переменную окружения:

```bash
export OPENROUTER_API_KEY="ваш_ключ_здесь"
```

Для постоянной установки добавьте в `~/.zshrc` или `~/.bash_profile`:

```bash
echo 'export OPENROUTER_API_KEY="ваш_ключ_здесь"' >> ~/.zshrc
source ~/.zshrc
```

### 6. Запуск

```bash
python main.py "Привет, объясни квантовые компьютеры"
```

Или с файлом:

```bash
python main.py --input request.txt --output result.txt
```

---

## Linux

### 1. Установка Python и Git

**Ubuntu / Debian:**

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv git
```

**Fedora / RHEL:**

```bash
sudo dnf install python3 python3-pip python3-virtualenv git
```

**Arch:**

```bash
sudo pacman -S python python-pip git
```

### 2. Скачать проект

```bash
git clone https://github.com/Addorax322/intgtool.git
cd intgtool
```

### 3. Создать виртуальное окружение

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Установить зависимости

```bash
pip install -r requirements.txt
```

### 5. Настроить конфиг и API-ключ

```bash
cp config.example.yaml config.yaml
```

Задайте переменную окружения:

```bash
export OPENROUTER_API_KEY="ваш_ключ_здесь"
```

Для постоянной установки (bash):

```bash
echo 'export OPENROUTER_API_KEY="ваш_ключ_здесь"' >> ~/.bashrc
source ~/.bashrc
```

### 6. Запуск

```bash
python main.py "Привет, объясни квантовые компьютеры"
```

Или с файлом:

```bash
python main.py --input request.txt --output result.txt
```

---

## Полезные команды

| Описание | Команда |
|----------|---------|
| Интерактивный чат | `python main.py` |
| Один запрос | `python main.py "текст запроса"` |
| Из файла в файл | `python main.py -i input.txt -o result.txt` |
| Стриминг в консоль | `python main.py --stream "запрос"` |
| Другая модель | `python main.py -m deepseek/deepseek-r1 "запрос"` |

---

## Обновление проекта

Если репозиторий уже скачан и нужно подтянуть изменения:

```bash
cd intgtool
git pull
pip install -r requirements.txt
```
