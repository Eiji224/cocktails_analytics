# Cocktails Analytics

Информационно-аналитическая система о коктейлях: каталог, подбор по ингредиентам, избранное и рейтинг популярности на основе просмотров. Данные берём из открытого API TheCocktailDB, сохраняем в MySQL, считаем метрики через Pandas и отображаем в Django-шаблонах.

## Что делает система
- Каталог и поиск коктейлей/ингредиентов, просмотр рецептов с инструкциями и изображениями.
- Избранное для авторизованных пользователей.
- Подсчет и отображение популярных коктейлей на основе просмотров (middleware в `analytics`).

## Технологический стек
- Python, Django 6, Django ORM
- MySQL 8
- Pandas для аналитики просмотров
- Requests для интеграции с TheCocktailDB
- Gunicorn + Nginx (в Docker Compose)
- Docker / Docker Compose
- Bootstrap для UI, статика в `static/`

## Основные модули
- `cocktails` — каталог напитков, ингредиенты, избранное, шаблоны страниц.
- `cocktails/management/commands/load_cocktails.py` — загрузка/обновление коктейлей из TheCocktailDB (`--refresh-existing` для перепарсинга существующих и пересборки связок ингредиентов).
- `analytics` — middleware для учета просмотров и отображение популярных коктейлей.
- `users` — регистрация/аутентификация (кастомная модель пользователя).

## Переменные окружения (.env)
Обязательные:
- `DJANGO_SECRET_KEY` — секрет Django.
- `ALLOWED_HOSTS` — список хостов через запятую, например `localhost,127.0.0.1`.
- `DOMAIN` — домен для CSRF-траста.
- `ADMIN_EMAIL` — почта для certbot.
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` — параметры MySQL (в Docker обычно `DB_HOST=db`, `DB_PORT=3306`).
- `MYSQL_ROOT_PASSWORD` — root-пароль MySQL (нужен контейнеру БД).
- `COCKTAIL_URL` — базовый URL поиска коктейлей по букве, напр. `https://www.thecocktaildb.com/api/json/v1/1/search.php?f=`.
- `INGREDIENT_URL` — базовый URL поиска ингредиента, напр. `https://www.thecocktaildb.com/api/json/v1/1/search.php?i=`.
- `INGREDIENT_IMAGE_URL` — базовый URL картинок ингредиентов, напр. `https://www.thecocktaildb.com/images/ingredients`.

Опционально:
- `DEBUG` — если хотите переопределить режим, иначе в settings стоит False.

## Запуск через Docker Compose
1) Создайте файл `.env` в корне со значениями переменных выше.  
2) Соберите контейнеры:  
   `docker compose build`  
3) Запустите:  
   `docker compose up -d`  
4) Выполните миграции:  
   `docker compose exec app python manage.py migrate`  
5) Соберите статику (для nginx):  
   `docker compose exec app python manage.py collectstatic --noinput`  
6) Загрузите данные из TheCocktailDB:  
   - только новые: `docker compose exec app python manage.py load_cocktails`  
   - перепарсить существующие и пересобрать связки ингредиентов:  
     `docker compose exec app python manage.py load_cocktails --refresh-existing`

## Локальный запуск без Docker
1) Установите MySQL и создайте БД/пользователя, заполните `.env` (DB_HOST=localhost, DB_PORT=3306 и т.д.).  
2) Установите зависимости:  
   `python -m venv .venv && source .venv/bin/activate`  
   `pip install -r requirements.txt`  
3) Примените миграции: `python manage.py migrate`  
4) (Опционально) Загрузите данные: `python manage.py load_cocktails [--refresh-existing]`  
5) Запустите dev-сервер: `python manage.py runserver`

## Полезные команды
- Создать суперпользователя: `docker compose exec app python manage.py createsuperuser`
- Пересоздать связи ингредиентов для существующих коктейлей: `python manage.py load_cocktails --refresh-existing`
- Проверить здоровье БД в контейнере: `docker compose ps`