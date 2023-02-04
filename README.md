# API YaMDB

Сервис  "YaMDB" - портал о фильмах, книгах и музыке, где пользователи могут оценивать и комментировать произведения.
Создано в рамках курса Яндекс.Практикум.

# Описание проекта

## Технологии
* Python, версия 3.8.10, Django REST Framework 2.2.16
* SimpleJWT - аутентификация по JWT-токену
* python-dotenv - хранение секретных ключей и доступ к ним через переменные окружения
* git - система управления версиями


## Как запустить проект:

Клонируйте репозиторий и перейдите в него в командной строке:

```
git clone https://github.com/SkyFlyer2/api_yamdb.git
```

```
cd api_yamdb
```

**С помощью Makefile:**
 
В терминале выполните команду `make setup`, 
после чего автоматически развернется виртуальное окружение, установятся необходимые пакеты.

**Если по какой-то причине Makefile не сработал, вы можете развернуть проект вручную:**

Cоздайте и активируйте виртуальное окружение:

```
python -m venv venv
```

```
source venv/Scripts/activate
```

Установите зависимости из файла requirements.txt:

```
python -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

**После создания окружения и установки пакетов:**

Создайте в директории файл .env и поместите туда SECRET_KEY, необходимый для запуска проекта

Выполните миграции:

```
python manage.py migrate
```

Создайте суперпользователя:

```
python manage.py createsuperuser
```

Запустите проект:

```
python manage.py runserver
```
____________________________________

Проект доступен по адресу `http://127.0.0.1:8000/`

Документация по API `http://localhost:8000/redoc/`

Командой `pytest` можно запустить тесты модулей


**Примеры API-запросов**

Запросы для всех пользователей

curl -H 'Accept: application/json' `http://127.0.0.1:8000/api/v1/titles/` - получить список всех произведений
curl -H 'Accept: application/json' `http://127.0.0.1:8000/api/v1/categories/` - получить список категорий
curl -H 'Accept: application/json' `http://127.0.0.1:8000/api/v1/genres/` - получить список жанров
curl -H 'Accept: application/json' `http://127.0.0.1:8000/api/v1/comments/` - получить список всех комментариев к записи


**Аутентификация:**

* Создать учетную запись:
curl --header "Content-Type: application/json" --request POST --data '{"username":"username","email":"email@email.com"}' `http://localhost:8000/api/v1/auth/signup/`

* После создания записи вы получите код подтверждения, по которому можно получить токен для авторизации:
curl --header "Content-Type: application/json" --request POST --data '{"username":"username","email":"email@email.com", "confirmation_code":"your_code"}' `http://localhost:8000/api/v1/auth/token/`

**Авторы:**

* Ковалев Владислав `https://github.com/SkyFlyer2` 
Управление пользователями (Auth и Users): система регистрации и аутентификации, права доступа, работа с токеном, система подтверждения e-mail.

* Евгений Шарашкин `https://github.com/sharashkin`
Категории (Categories), жанры (Genres) и произведения (Titles): модели, view и эндпойнты для них.

* Белов Андрей `https://github.com/m9yrizzo`
Отзывы (Review) и комментарии (Comments): модели и view, эндпойнты, права доступа для запросов. Рейтинги произведений.
