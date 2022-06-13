import json
from datetime import datetime
from uuid import UUID

from django.test import TestCase, Client

from products.models import Product, ProductHistory


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.category_obj = Product.objects.create(
            id=UUID('4fa85f64-5717-4562-b3fc-2c963f66a444'),
            name='TestNameCategory',
            date=datetime.now(),
            type='CATEGORY'
        )

        cls.category_obj2 = Product.objects.create(
            id=UUID('4fa85f64-5717-4562-b3fc-2c963f66a111'),
            name='TestNameCategory2',
            date=datetime.now(),
            parentId=cls.category_obj,
            type='CATEGORY'
        )

        cls.offer_obj = Product.objects.create(
            id=UUID('4fa85f64-5717-4562-b3fc-2c963f66a999'),
            name='TestNameOffer',
            date=datetime.strptime("2022-05-28T21:12:01.000Z", "%Y-%m-%dT%H:%M:%S.%fZ"),
            type='OFFER',
            price=1,
            parentId=cls.category_obj2
        )

        cls.offer_obj2 = Product.objects.create(
            id=UUID('4fa85f64-5717-4562-b3fc-2c963f66a101'),
            name='TestNameOffer',
            date=datetime.strptime("2022-05-28T21:12:01.000Z", "%Y-%m-%dT%H:%M:%S.%fZ"),
            type='OFFER',
            price=100,
            parentId=cls.category_obj2
        )

    def setUp(self):
        self.guest_client = Client()
        self.request_data_offer_as_parent = json.dumps(
            {
                "items": [
                    {
                        "id": "4fa85f64-5717-4562-b1fc-2c963f66a333",
                        "name": "Оффер",
                        "parentId": "4fa85f64-5717-4562-b3fc-2c963f66a999",
                        "price": 50,
                        "type": "OFFER"
                    }
                ],
                "updateDate": "2022-05-28T21:12:01.000Z"
            })

        self.request_data_double_offer_import = json.dumps(
            {
                "items": [
                    {
                        "id": "4fa85f64-5717-4562-b1fc-2c963f66a333",
                        "name": "Оффер",
                        "parentId": "4fa85f64-5717-4562-b3fc-2c963f66a111",
                        "price": 23451,
                        "type": "OFFER"
                    },
                    {
                        "id": "5fa85f64-5717-4562-b1fc-2c963f66a333",
                        "name": "Оффер",
                        "parentId": "4fa85f64-5717-4562-b3fc-2c963f66a111",
                        "price": 1111,
                        "type": "OFFER"
                    }
                ],
                "updateDate": "2022-05-28T21:12:01.000Z"
            })
        self.request_data_offer_obj_update_import = json.dumps(
            {
                "items": [
                    {
                        "id": "4fa85f64-5717-4562-b3fc-2c963f66a999",
                        "name": "test_history",
                        "price": 11,
                        "type": "OFFER"
                    }
                ],
                "updateDate": "2022-07-01T21:12:01.000Z"
            })

        self.request_data_offer_obj_update_import2 = json.dumps(
            {
                "items": [
                    {
                        "id": "4fa85f64-5717-4562-b3fc-2c963f66a999",
                        "name": "test_history",
                        "price": 1000,
                        "type": "OFFER"
                    }
                ],
                "updateDate": "2022-05-27T21:12:01.000Z"
            })

        self.request_data_category_import = json.dumps(
            {
                "items": [
                    {
                        "id": "4fa85f64-5717-4562-b3fc-2c963f66a999",
                        "name": "test_c",
                        "type": "CATEGORY"
                    }
                ],
                "updateDate": "2022-05-28T21:12:01.000Z"
            })

        self.request_data_offer_import = json.dumps(
            {
                "items": [
                    {
                        "id": "4fa85f64-5717-4562-b3fc-2c963f66a991",
                        "name": "test_o",
                        "type": "OFFER"
                    }
                ],
                "updateDate": "2022-05-28T21:12:01.000Z"
            })

    def test_delete_category(self):
        url = '/delete/4fa85f64-5717-4562-b3fc-2c963f66a444'
        response = self.guest_client.delete(url)
        self.assertEqual(response.status_code, 200, 'Удаление продукта не работает')

        child_offer = Product.objects.filter(parentId__id=UUID('4fa85f64-5717-4562-b3fc-2c963f66a444')).exists()
        self.assertEqual(child_offer, False, 'При удалении категории не удаляются дочерние товары')

    def test_import_product(self):
        response = self.guest_client.post('/imports', self.request_data_double_offer_import,
                                          content_type="application/json")
        self.assertEqual(response.status_code, 200, 'Продукт не добавляется')

        # Дополнительный запрос необходим, поскольку объекты из setUpClass не изменяются
        # при обновлении их дочерних элементов, если получать доступ к ним через 'self.obj'
        url = '/nodes/4fa85f64-5717-4562-b3fc-2c963f66a111'
        response_retrieve = self.guest_client.get(url)
        self.assertEqual(response_retrieve.data.get('date'), "2022-05-28T21:12:01.000Z",
                         'Дата последнего изменения категории после добавления товара не меняется')
        # Проверка на то, можно ли добавить товар в качестве категории
        response = self.guest_client.post('/imports', self.request_data_offer_as_parent,
                                          content_type="application/json")
        self.assertEqual(response.status_code, 400, 'Товар не может быть родителем')

    def test_product_history(self):
        self.guest_client.post('/imports', self.request_data_offer_obj_update_import,
                               content_type="application/json")
        history_obj = ProductHistory.objects.get(product_id=self.offer_obj.id,
                                                 name='test_history')
        self.assertEqual(history_obj.name, 'test_history')
        self.assertEqual(history_obj.price, 11)
        self.assertIsNone(history_obj.parentId)
        self.assertEqual(history_obj.date, datetime.strptime("2022-07-01T21:12:01.000Z", "%Y-%m-%dT%H:%M:%S.%fZ"))
        self.assertTrue(history_obj.price_changed)
        self.assertEqual(history_obj.type, 'OFFER')

        old_history_obj = ProductHistory.objects.get(product_id=self.offer_obj.id,
                                                     name='TestNameOffer')
        self.assertEqual(old_history_obj.name, self.offer_obj.name)
        self.assertEqual(old_history_obj.price, self.offer_obj.price)
        self.assertEqual(old_history_obj.parentId, self.offer_obj.parentId)
        self.assertEqual(old_history_obj.date, self.offer_obj.date)
        self.assertFalse(old_history_obj.price_changed)
        self.assertEqual(old_history_obj.type, self.offer_obj.type)

    def test_product_retrieve(self):
        url = '/nodes/4fa85f64-5717-4562-b3fc-2c963f66a444'
        response = self.guest_client.get(url)
        # Проверяет наличие дочерных элементов в ответе
        self.assertEqual(response.data.get('name'), 'TestNameCategory')
        self.assertEqual(response.data.get('children')[0].get('name'), 'TestNameCategory2')
        self.assertEqual(response.data.get('children')[0].get('children')[0].get('name'), 'TestNameOffer')
        # Проверяет правильность формирования цены родительской категории
        self.assertEqual(response.data.get('price'), 50)
        # Проверяет праильность и наличие всех возвращенных полей в ответе
        fields = ['name', 'id', 'parentId', 'date', 'price', 'type', 'children']
        for _ in range(len(fields)):
            field = fields.pop()
            self.assertTrue(field in response.data.keys(),
                            f'Не вернулось поле - "{field}"')

    def test_price_value(self):
        self.guest_client.post('/imports', self.request_data_category_import,
                               content_type="application/json")
        category_obj = Product.objects.get(id=UUID('4fa85f64-5717-4562-b3fc-2c963f66a999'))
        self.assertIsNone(category_obj.price, 'При создании категории без указания цены, цена должна быть == None')

        self.guest_client.post('/imports', self.request_data_offer_import,
                               content_type="application/json")
        offer_obj = Product.objects.get(id=UUID('4fa85f64-5717-4562-b3fc-2c963f66a991'))
        self.assertEqual(offer_obj.price, 0, 'При создании товара без указания цены, цена должна быть == 0')

    def test_sales(self):
        self.guest_client.post('/imports', self.request_data_offer_obj_update_import2,
                               content_type="application/json")
        url = '/sales?date=2022-05-28T21:12:01.000Z'
        response = self.guest_client.get(url)
        self.assertEqual(len(response.data.get('items')), 1)

        self.guest_client.post('/imports', self.request_data_offer_obj_update_import,
                               content_type="application/json")
        url = '/sales?date=2022-05-28T21:12:01.000Z'
        response = self.guest_client.get(url)
        self.assertEqual(len(response.data.get('items')), 1)

    def test_statistic(self):
        url = '/node/4fa85f64-5717-4562-b3fc-2c963f66a999/statistic'
        response = self.guest_client.get(url)
        self.assertEqual(len(response.data.get('items')), 1)
        # Обновляем запись
        self.guest_client.post('/imports', self.request_data_offer_obj_update_import,
                               content_type="application/json")
        # В истории должна была появиться вторая запись
        response2 = self.guest_client.get(url)
        self.assertEqual(len(response2.data.get('items')), 2,
                         'В истории продукта не сохраняются данные об обновлении модели')
        # В данном временном диапазоне находится лишь объект, который был обновлен ранее
        url_with_date_range = ('/node/4fa85f64-5717-4562-b3fc-2c963f66a999/statistic'
                               '?dateStart=2022-06-01T21:12:01.000Z&dateEnd=2022-07-03T00:00:00.000Z')
        response3 = self.guest_client.get(url_with_date_range)
        self.assertEqual(len(response3.data.get('items')), 1,
                         'Статистика по временному диамазону отдается некорректно')
