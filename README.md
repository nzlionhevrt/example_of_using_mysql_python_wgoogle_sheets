# Тестовое задание: MySQL + Python + Google Sheets + Yandex DataLens

Проект для интеграции данных из Google Sheets в MySQL и визуализации в Yandex DataLens.

## Структура проекта

- `docker-compose.yml` - конфигурация для запуска MySQL
- `init.sql` - SQL скрипт для инициализации БД и таблиц
- `load_plan_from_sheets.py` - Python скрипт для загрузки данных из Google Sheets
- `requirements.txt` - зависимости Python
- `env.example` - пример файла с настройками
- `install_docker.sh` - скрипт для установки Docker и Docker Compose

## Требования

- Docker и Docker Compose
- Python 3.8+

## Установка и запуск

### 0. Установка Docker и Docker Compose

Если Docker и Docker Compose еще не установлены, используйте скрипт установки:

```bash
sudo bash install_docker.sh
```

Или установите вручную по [официальной документации Docker](https://docs.docker.com/engine/install/).

После установки проверьте:

```bash
docker --version
docker compose version
```

### 1. Запуск MySQL через Docker Compose

```bash
docker-compose up -d
```

MySQL будет доступен на порту 3306.

### 2. Настройка окружения

Скопируйте `env.example` в `.env` и заполните настройки:

```bash
cp env.example .env
```

Отредактируйте `.env`:
- `MYSQL_PASSWORD` - пароль для пользователя MySQL (по умолчанию: analytics_password)
- `GOOGLE_SHEETS_URL` - URL вашей Google таблицы

### 3. Установка зависимостей Python

```bash
pip install -r requirements.txt
```

### 4. Подготовка Google Sheets

1. Создайте Google таблицу со следующей структурой:
   - Колонки: `month`, `club_id`, `club_name`, `plan_revenue`
   - Пример данных:
     ```
     month       | club_id | club_name | plan_revenue
     2025-09-01  | 1       | Club A    | 5000000
     2025-09-01  | 2       | Club B    | 4000000
     2025-09-01  | 3       | Club C    | 3500000
     ```

2. Опубликуйте таблицу для общего доступа:
   - Файл → Опубликовать в интернете
   - Выберите формат CSV
   - Скопируйте ссылку и укажите её в `.env` как `GOOGLE_SHEETS_URL`

### 5. Запуск скрипта загрузки данных

```bash
python load_plan_from_sheets.py
```

Скрипт выполнит:
- Чтение данных из Google Sheets
- Подключение к MySQL
- UPSERT данных в таблицу `revenue_plan` (обновление существующих или вставка новых записей)

## Примечания

- Для работы скрипта Google Sheets должна быть опубликована для общего доступа
- Скрипт автоматически обрабатывает форматирование чисел (удаляет пробелы и запятые)
- При повторном запуске скрипта существующие записи обновляются (UPSERT)


