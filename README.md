# YaMDb

Социальный интернет сервис с народными рецензиями о фильмах, книгах и музыке.

- создавайте ревью!
- ставьте рейтинги!
- комментируйте!
- творите чудеса! ✨✨✨

### Возможности

\- регистрируйтесь на сайте и создавайте ревью!
\- ставьте рейтинги различным произведениям!
\- комментируйте другие ревью!
\- творите словесные чудеса! ✨✨✨

> “Всякая мысль, выраженная словами, есть сила, действие которой беспредельно.”
\- [Лев Толстой](https://ru.wikipedia.org/wiki/Толстой,_Лев_Николаевич)

> “Нужны такие слова, которые бы звучали, как колокол набата, тревожили все и, сотрясая, толкали вперед.”
\- [Максим Горький](https://ru.wikipedia.org/wiki/Максим_Горький)

### Технологии

Yatube API uses a number of open source projects to work properly:

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) ![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white) ![DjangoREST](https://img.shields.io/badge/DJANGO-REST-ff1709?style=for-the-badge&logo=django&logoColor=white&color=ff1709&labelColor=gray) ![JWT](https://img.shields.io/badge/JWT-black?style=for-the-badge&logo=JSON%20web%20tokens)
- [Python] (v.3.9) - целевой язык программирования
- [Django] (v.3.2) - высокоуровневый веб-фреймворк
- [Django REST framework] (v.3.12.4) - инструмент для создания Web API
- [Simple JWT] (v.2.1.0) - плагин, предоставляющий JSON Web Token аунтификацию для Django REST Framework, разработанную в соответствии со стандартом RFC 7519

### Установка

Перейти в целевую папку и склонировать репозиторий

```sh
git clone https://github.com/Altair21817/api_yamdb.git
```

Создать виртуальное окружение

> Windows

```sh
python -3.9 -m venv venv
```

> Linux

```sh
python3 -m venv venv
```

> MacOS

```sh
brew link python@3.9
```

Активировать виртуальное окружение

```sh
sourse venv/scripts/activate
```

Обновить инсталлятор pip

```sh
python -m pip install --upgrade pip
```

Установить зависимости из requirements.txt

```sh
pip install -r requirements.txt
```

Перейти в рабочую папку проекта

```sh
cd yatube_api/yatube_api/
```

Создать миграции

```sh
python manage.py migrate
```

Запустить сервер

```sh
python3 manage.py runserver
```

Убедиться в успешном развертывании приложения, перейдя по ссылке ниже

```sh
127.0.0.1:8000
```

### Некоторые примеры запросов и ответов

- получить список всех произведений

request

```sh
GET http://127.0.0.1:8000/api/v1/titles/ HTTP/1.1
```

response

```sh
{
    "count": 0,
    "next": "string",
    "previous": "string",
    "results": [
        {
            "id": 0,
            "name": "string",
            "year": 0,
            "rating": 0,
            "description": "string",
            "genre": [],
            "category": {}
        }
        ...
    ]
}
```

- добавить произведение

request

```sh
POST http://127.0.0.1:8000/api/v1/posts/ HTTP/1.1
Content-Type: application/json
Authorization: Bearer eyJ0...5fqU

{
    "name": "string: название, обязательное поле!",
    "year": "integer: год выпуска, обязательное поле!",
    "description": "string: описание",
    "genre": "array of strings: жанр (slug поле), обязательное поле!",
    "category": "string: категория (slug поле), обязательное поле!"
}
```

response

```sh
{
    "name": "название",
    "year": "год выпуска",
    "description": "описание",
    "genre": "жанр",
    "category": "категория"
}
```

**Полна документация доступна в OpenAPI ReDoc!**

### Разработка

Хотите внести вклад в разработку проекта? Замечательно! Свяжитесь со мной по адресу some@imail.com!

### Лицензия

MIT

**Free Software, Hell Yeah!**
Created by [Altair21817], [Azerothforev], [MucharaKonstantin]

[Altair21817]: <https://github.com/Altair21817>
[Azerothforev]: <https://github.com/Azerothforev>
[MucharaKonstantin]: <https://github.com/MucharaKonstantin>
[Python]: <https://www.python.org/>
[Django]: <https://www.djangoproject.com/>
[Django REST framework]: <https://https://www.django-rest-framework.org/>
[Simple JWT]: <https://django-rest-framework-simplejwt.readthedocs.io/en/latest/>