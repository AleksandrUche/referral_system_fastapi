### О проекте

RESTFull API сервис для реферальной системы, который позволяет пользователям
регистрироваться, аутентифицироваться и создавать или удалять свой реферальный код,
а также регистрироваться с реферальным кодом.

### Технологический стек:

- FastAPI
- SQLAlchemy 2.0
- AsyncIO
- JWT для аутентификации
- OAuth 2.0

### Для запуска приложения выполнить следующие шаги:

1. Если у вас еще не установлен poetry — установите с помощью команды:
   ```pip install poetry```.
2. Находясь в директории проекта с файлом pyproject.toml, установить зависимости с
   помощью команды: ```poetry install```.
3. Необходимо поднять postgresql с помощью команды:

```
docker run -p 5432:5432 --name postgres_referral -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=12345 -e POSTGRES_DB=postgres -d postgres:13.1
```

4. Создайте файл ```.env``` по примеру файла ```.env-example```
5. Проведите миграции: ```alembic upgrade head```.
6. Запуск приложения: ```uvicorn app.main:app --reload```.

### Postman

Для работы с Postman, можете импортировать файл
```referrals fast api.postman_collection.json```, он находится в главной директории.