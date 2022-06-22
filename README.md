# Вступительное задание в Академию Яндекса
* Проект развернут тут - `https://nick-2016.usr.yandex-academy.ru`
* Спецификация API описана в файле `openapi.yaml` в корневой папке проекта. (https://editor.swagger.io/)

## Локальный запуск проекта через docker compose
Создайте файл `.env` и заполните его в соответствии с перечисленными полями в файле `env_example.txt` в корневой папке проекта. 
Из корневой папки выполните:
``` python
docker-compose up --build
docker-compose run backend python manage.py makemigrations
docker-compose run backend python manage.py migrate
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
pip3 install -r requirements.txt
```
Из попки `/config` выполните:
```python
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py runserver
```
Проект будет запущен на `http://127.0.0.1:8000/`


### Запуск тестов:
```python
# Запуск через docker compose
docker-compose run backend python manage.py test
# Для запуска с sqlite3
python3 manage.py test
```

### Создание суперпользователя:
```python
# Запуск через docker compose
docker-compose run backend python manage.py createsuperuser
# Для запуска с sqlite3
python3 manage.py createsuperuser
```
Админка доступна по адресу - `/admin`

## Устройство и работа кода
Сервис написан на Django Rest Framework.

### Модели 
Находятся в /products/models.py
* Модель `Product` содержит данные о товарах и категориях, которые добавляют пользователи.
* Модель `ProductHistory` содержит данные об истории изменения товара.
* При добавлении товара/категории срабатывает сигнал `pre_save_product_receiver`, который сохраняет сохраняет новые данные в историю товара. Если товар был обновлен, проверяет изменилась ли цена товара и устанавливает нужно значение флажку `price_changed`.
* При удалении продукта/категории срабатывает `pre_delete_product_receiver`, который очистит всю историю изменений удаляемого продукта, а также, в случае если была удалена категория, удалит все дочерние элементы данной категории.

### Сериализаторы
Находятся в `/products/serializers.py`
* Отвечают за сериализацию и десериализацию данных.
* Поля `ModelSerializer` валидируют корректность входных данных.
* Метод `validate` валидирует отдельные случаи.
###### `ProductCreateUpdateDeleteSerializer` отвечает за сериализацию данных запросов, поступающих на `/imports` и `/delete/{id}`
* Во время создания и обновления объекта вызывается метод `create`. Если объект уже создан, то данные существующего объекта и входящие данные передаются в метод `update`,  который обновляет все поля продукта.
###### `ProductRetrieveSerializer` обрабатывает `retrieve` запросы к `/nodes/{id}`
* Метод `get_children` рекурсивно возвращает дочерние элементы категорий.
* Поскольку категории не хранят среднее значение стоимости их дочерних товаров, вычисление средней стоимости происходит в методе `get_price`, в случае когда нужно десериализовать данные категории. Дочерние категории можно получить использовав `related_name` модели `Product` - `child.children.all()`.
###### `SalesProductSerializer` работает с запросами, поступаюющими на `/sales` и `/node/{id}/statistic`.

### Представления
Находятся в `/products/views.py`
###### `ProductViewSet` работает со всеми запросами, поступающими к API. 
* В зависимости от метода запроса, метод `get_serializer_class` выбирает необходимый сериализатор, в который отправятся данные. Методы `statistic` и `sales` явно используют `SalesProductSerializer`.
* `сreate` срабатывает при обращении к `/imports/`. Сначала создаются категории, потом создаются товары, чтобы категории можно было использовать в качестве родителя для товаров из того же запроса.
* `destroy` переопределен, чтобы возвращать 200-й статус код.
* `statistic` парсит дату из `request`, получает данные об истории изменения объекта за представленный период, отправляет данные в сериализатор.
### Админка
* Сервис работает без `Nginx`, вследствии чего на страницу админки не раздаётся статика.
Статика админки будет работать, если запустить сервер локально без `docker`.









