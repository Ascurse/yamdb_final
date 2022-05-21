# yamdb_final
# Проект YaMDb
## Описание
Проект YaMDb собирает отзывы (Review) пользователей на произведения (Titles). Произведения делятся на категории: "Книги", "Фильмы", "Музыка". Список категорий (Category) может быть расширен администратором (например, можно добавить категорию "Ювелирка").

### Технологии
- Python 3.7
- Django 2.2.19
- DRF, JWT
- Docker
- Nginx

### Руководство по запуску проекта:

Клонировать репозиторий:

```bash
git clone https://github.com/Ascurse/infra_sp2.git
```
Либо, если используете доступ к Github через SSH:
```bash
git clone git@github.com:Ascurse/infra_sp2.git
```
Перейти в склонированный репозиторий:
```bash
cd infra_sp2/
```

Cоздать и активировать виртуальное окружение:

```bash
python -m venv env
```

```bash
source env/bin/activate
```

```bash
python -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```bash
pip install -r requirements.txt
```

Запустить приложение в контейнерах:

*из директории `infra/`*
```bash
docker-compose up -d --build
```

Выполнить миграции:

*из директории `infra/`*
```bash
docker-compose exec web python manage.py migrate
```

Создать суперпользователя:

*из директории `infra/`*
```bash
docker-compose exec web python manage.py createsuperuser
```

Собрать статику:

*из директории `infra/`*
```bash
docker-compose exec web python manage.py collectstatic --no-input
```

Остановить приложение в контейнерах:

*из директории `infra/`*
```bash
docker-compose down -v
```
Запуск `pytest`:

*при запущенном виртуальном окружении*
```bash
cd infra_sp2 && pytest
```
### Создайте файл .env (пример заполнения находится в файле env.example):
DB_ENGINE= # указываем с какой базой данных работаем
DB_NAME= # имя базы данных
POSTGRES_USER= # логин для подключения к базе данных
POSTGRES_PASSWORD= # пароль для подключения к БД (установите свой)
DB_HOST= # название сервиса (контейнера)
DB_PORT= # порт для подключения к БД

### Документация API с примерами:

```json
/redoc/
```

### Описание команды для заполнения базы данными
```bash
cd api_yamdb && python manage.py loaddata ../infra/fixtures.json
```
![example workflow](https://github.com/Ascurse/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)