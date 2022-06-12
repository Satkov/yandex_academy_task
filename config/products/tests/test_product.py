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
        cls.offer_obj = Product.objects.create(
            id=UUID('4fa85f64-5717-4562-b3fc-2c963f66a999'),
            name='TestNameOffer',
            date=datetime.now(),
            type='OFFER',
            price=100
        )

    def setUp(self):
        self.guest_client = Client()

    def test_delete_product(self):
        url = '/delete/4fa85f64-5717-4562-b3fc-2c963f66a444'
        response = self.guest_client.delete(url)
        self.assertEqual(response.status_code, 200, 'Удаление продукта не работает')

    def test_import_product(self):
        request_data = json.dumps({
            "items": [
                {
                    "id": "4fa85f64-5717-4562-b1fc-2c963f66a333",
                    "name": "Оффер",
                    "parentId": "4fa85f64-5717-4562-b3fc-2c963f66a444",
                    "price": 23451,
                    "type": "OFFER"
                },
                {
                    "id": "5fa85f64-5717-4562-b1fc-2c963f66a333",
                    "name": "Оффер",
                    "parentId": "4fa85f64-5717-4562-b3fc-2c963f66a444",
                    "price": 1111,
                    "type": "OFFER"
                }
            ],
            "updateDate": "2022-05-28T21:12:01.000Z"
        })
        response = self.client.post('/imports', request_data,
                                    content_type="application/json")
        self.assertEqual(response.status_code, 200, 'Продукт не добавляется')

    def test_product_history(self):
        request_data = json.dumps({
            "items": [
                {
                    "id": "4fa85f64-5717-4562-b3fc-2c963f66a999",
                    "name": "test_history",
                    "price": 11,
                    "type": "OFFER"
                }
            ],
            "updateDate": "2022-05-28T21:12:01.000Z"
        })
        self.client.post('/imports', request_data,
                         content_type="application/json")

        history_obj = ProductHistory.objects.get(product_id=self.offer_obj.id,
                                                 name='test_history')
        self.assertEqual(history_obj.name, 'test_history')
        self.assertEqual(history_obj.price, 11)
        self.assertEqual(history_obj.parentId, None)
        self.assertEqual(history_obj.date, datetime.strptime("2022-05-28T21:12:01.000Z", "%Y-%m-%dT%H:%M:%S.%fZ"))
        self.assertEqual(history_obj.price_changed, True)
        self.assertEqual(history_obj.type, 'OFFER')

        old_history_obj = ProductHistory.objects.get(product_id=self.offer_obj.id,
                                                     name='TestNameOffer')
        self.assertEqual(old_history_obj.name, self.offer_obj.name)
        self.assertEqual(old_history_obj.price, self.offer_obj.price)
        self.assertEqual(old_history_obj.parentId, self.offer_obj.parentId)
        self.assertEqual(old_history_obj.date, self.offer_obj.date)
        self.assertEqual(old_history_obj.price_changed, False)
        self.assertEqual(old_history_obj.type, self.offer_obj.type)
