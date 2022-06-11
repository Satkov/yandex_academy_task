from datetime import datetime

from django.http import Http404
from rest_framework.exceptions import ValidationError

from .models import ProductHistory


def SplitCategoriesFromOffers(request_data):
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
            obj_data['parentId'] = obj.parentId.id
        history.append(obj_data)
    return history


def ChangeParentDate(parent, new_date):
    while parent:
        parent.date = new_date
        parent.save()
        parent = parent.parentId


def GetProductHistoryDateRangeQueryset(pk, start, end):
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
