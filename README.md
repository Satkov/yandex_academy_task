# Вступительное задание в Академию Яндекса
* Проект развернут тут - `https://nick-2016.usr.yandex-academy.ru`
* Спецификация API описана в файле `openapi.yaml` в корневой папке проекта. (https://editor.swagger.io/)
* Все описанные команды выполняются на `python 3.7`

## Локальный запуск проекта через docker compose
Создайте файл `.env` и заполните его в соответствии с перечисленными полями в файле `env_example.txt` в корневой папке проекта. 
Из корневой папки выполните:
``` python
docker compose up --build
docker compose exec -it backend python manage.py makemigrations
docker compose exec -it backend python manage.py migrate
```
Проект будет запущен на `http://127.0.0.1/`

## Локальный запуск на sqlite3
В файле `/config/config/setting.py` замените переменную `DATABASES` на: 

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
```
Из корневой папки выполните:
``` python
pip install -r requirements.txt
```
Находясь в папке `/config` выполните:
```python
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```
Проект будет запущен на `http://127.0.0.1:8000/`


### Запуск тестов:
```python
# Запуск через docker compose
docker compose exec -it backend python manage.py test
# Для запуска с sqlite3
python manage.py test
```

### Создание суперпользователя:
```python
# Запуск через docker compose
docker compose exec -it backend python manage.py createsuperuser
# Для запуска с sqlite3
python manage.py createsuperuser
```
Админка доступна по адресу - `/admin`

## Устройство и работа кода
Сервис написан на базе Django Rest Framework.
Здесь описаны моменты, которые могут показаться неочевидными.

### Модели 
Находятся в /products/models.py
* Модель `Product` содержит данные о товарах и категориях, которые добавляют пользователи.
* Модель `ProductHistory` содержит данные об истории изменения товара.
* При добавлении товара/категории срабатывает сигнал `pre_save_product_receiver`, который сохраняет сохраняет новые данные в историю товара. Если товар был обновлен, проверяет изменилась ли цена товара и устанавливает нужно значение флажку `price_changed`.
* При удалении продукта/категории срабатывает `pre_delete_product_receiver`, который очистит всю историю изменений удаляемого продукта, а также, в случае если была удалена категория, удалит все дочерние элементы данной категории.

### Сериализаторы
Находятся в `/products/serializers.py`

* При сериализации данных для создания объкта `Product` в `ProductCreateUpdateDeleteSerializer` вызывается метод `create`, в случае, если объект уже есть в базе, данные существующего объекта и обновленные данные передаются в метод `update`, который обновляет все поля продукта.

* Метод `get_children` `ProductRetrieveSerializer'a` рекурсивно возвращает дочернии элементы категорий.

### Админка
* Сервис работает без `Nginx`, вследствии чего на страницу админки не раздаётся статика.
Статика админки будет работать, если запустить сервер локально без `docker`.









