Этот темплейт используется для разработки Telegram ботов с использованием библиотеки ['aiogram v3.0+'] (https://github.com/aiogram/aiogram/tree/dev-3.x).

## SQLAlchemy + Alembic
В коде есть примеры таблички User с использованием SQLAlchemy 2.0, и скрипты для алембика (инициализация алембик, создание и применение миграций).

Но, если вы с этими инструментами никогда не работали, то обратитесь к документации и узнайте об этих инструментах.
Также, у меня есть англоязычный [курс по этим инструментам на Udemy](https://www.udemy.com/course/sqlalchemy-alembic-bootcamp/?referralCode=E9099C5B5109EB747126).

![img.png](https://img-c.udemycdn.com/course/240x135/5320614_a8af_2.jpg)

### Для того, чтобы начать использовать:
1. скопируйте `.env.dist 'в'.env ' и заполните необходимые данные.
2. создайте новые хэндлеры.
3. **Docker:**
1. Можете сразу запускать проект из Docker, а если у вас его нет, то [загрузите, и установите](https://docs.docker.com/get-docker/).
2. запустите проект из команды ' docker-compose up`
4. * * Без Докера:**
1. Создайте [venv](https://docs.python.org/3/library/venv.html)
2. установит зависимости с requirements.txt: `pip install -r requirements.txt --pre`
3. запустите проект из команды ' python3 bot.py`


### Как делать и регистрировать хэндлеры:
Создаете модуль `you_name.py 'в папке 'handlers'.

Создаете роутер в `you_name.py`.
```python
from aiogram import Router
user_router = Router()
```
Можно делать несколько роутеров в одном модуле, и на каждый из них навешивать хэндлеры.
Можно регистрировать хэндлеры декораторами:
```python
@user_router.message(commands=["start"])
async def user_start(message):
await message.reply ("поздравляю, обычный пользователь!")
```

Заходим в файл `handlers/__init__.py ' и добавляем все роутеры в него:
```python
from .admin import admin_router
from .echo import echo_router
from .user import user_router

...


routers_list = [
admin_router,
user_router,
echo_router, # echo_router must be last
]

```
### Как добавить хэндлеры к нашему боту:
Переходим к файлу `bot.py ' и распаковываем наши хэндлеры:
```python
from tgbot.handlers import routers_list

...

async def main():

...

dp.include_routers(*routers_list)

...


```

### Туториалы с aiogram v3
Видосов пока нет, но @Groosha уже начал делать [свой учебник](https://mastergroosha.github.io/aiogram-3-guide).