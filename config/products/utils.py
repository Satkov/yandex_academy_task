from datetime import datetime

from django.http import Http404
from rest_framework.exceptions import ValidationError

from .models import ProductHistory


def SplitCategoriesFromOffers(request_data):
    """
    :param request_data: List[dict{}]
    :return: List[dict{}], List[dict{}]
    """
    CATEGORIES = []
    OFFERS = []
    for obj_data in request_data['items']:
        obj_data['date'] = request_data.get('updateDate')
        if obj_data.get('type') == 'CATEGORY':
            CATEGORIES.append(obj_data)
        else:
            OFFERS.append(obj_data)
    return CATEGORIES, OFFERS


def ParseDateFromRequest(request, field_name):
    """
    :param request: request obj
    :param field_name: str
    :return: Datetime
    """
    date = request.GET.get(field_name)
    if date is None:
        return None

    try:
        date = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ")
    except ValueError:
        raise ValidationError({
            'code': 400,
            'message': f'Wrong date format: {date}'
        })

    return date


def PutProductHistoryDataIntoDict(queryset):
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


def ChangeParentDate(parent, new_date):
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


def GetProductHistoryDateRangeQueryset(pk, start, end):
    """
    :param pk: UUID
    :param start: Datetime
    :param end: Datetime
    :return: queryset

    Если в функцию рередан временной диапазон, -
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
            "message": "Validation Failed"
        })

    return queryset
