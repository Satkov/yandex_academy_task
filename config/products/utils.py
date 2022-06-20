from datetime import datetime

from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError

from .models import Product, ProductHistory


def split_categories_from_offers(request_data):
    """
    :param request_data: List[dict{}]
    :return: List[dict{}], List[dict{}]
    """
    categories = []
    offers = []
    for obj_data in request_data['items']:
        obj_data['date'] = request_data.get('updateDate')
        if obj_data.get('type') == 'CATEGORY':
            categories.append(obj_data)
        else:
            offers.append(obj_data)
    return categories, offers


def parse_date_from_request(request, field_name, raise_exceptions=False):
    """
    :param raise_exceptions: bool
    :param request: request obj
    :param field_name: str
    :return: Datetime
    """
    date = request.GET.get(field_name)
    if date is None:
        if raise_exceptions:
            raise ValidationError({
                'code': 400,
                'message': "Date was't given"
            })
        return None

    try:
        date = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ")
    except ValueError:
        raise ValidationError({
            'code': 400,
            'message': f'Wrong date format: {date}'
        })

    return date


def get_product_objs_by_ids_from_product_history(queryset):
    """
    :param queryset: queryset(ProductHistory)
    :return: List[dict{}]
    """
    d = {}
    product_objs = []
    for history_obj in queryset:
        history_id = history_obj.product_id
        if history_id not in d:
            d[history_id] = True
            product = get_object_or_404(Product, id=history_id)
            data = {
                'name': product.name,
                'id': product.id,
                'parentId': product.parentId,
                'date': product.date,
                'price': product.price,
                'type': product.type,
            }
            product_objs.append(data)
    return product_objs


def put_product_history_data_into_dict(queryset):
    """
    :param queryset: queryset
    :return: list[dict{}]
    """
    history = []
    for obj in queryset:
        obj_data = {
            'id': obj.product_id,
            'name': obj.name,
            'date': obj.date,
            'type': obj.type,
            'price': obj.price
        }
        if obj.parentId:
            # Если передать None, сериализатор выдаст ошибку
            obj_data['parentId'] = obj.parentId.id
        history.append(obj_data)
    return history


def change_parent_dates(parent, new_date):
    """
    parent: Product obj
    new_date: Datetime

    После обновления товара,
    меняет дату последнего обновления его категорий.
    """
    while parent:
        parent.date = new_date
        parent.save()
        parent = parent.parentId


def get_product_history_date_range_queryset(pk, start, end):
    """
    :param pk: UUID
    :param start: Datetime
    :param end: Datetime
    :return: queryset

    Если в функцию передан временной диапазон, -
    вернет историю изменений объекта за указанное время.
    Если диапазон не указан, - вернет всю историю.
    """
    if not ProductHistory.objects.filter(product_id=pk).exists():
        raise Http404({
            "code": 404,
            "message": "Item not found"
        })
    if not start:
        queryset = ProductHistory.objects.filter(product_id=pk)
    else:
        queryset = ProductHistory.objects.filter(product_id=pk,
                                                 date__range=[start, end])

    if not queryset:
        raise ValidationError({
            "code": 400,
            "message": "No items in this date range"
        })

    return queryset
