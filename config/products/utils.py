from datetime import datetime

from rest_framework.exceptions import ValidationError


def get_request_data(context):
    """
    Проверяет, есть ли контекст в request
    """
    try:
        request = context.get('request_data')
    except KeyError:
        raise KeyError({
            'error': 'request was not received'
        })
    return request


def SplitCategoriesFromOffers(request_data):
    CATEGORIES = []
    OFFERS = []
    for obj_data in request_data:
        if obj_data.get('type') == 'CATEGORY':
            CATEGORIES.append(obj_data)
        else:
            OFFERS.append(obj_data)

    return CATEGORIES, OFFERS


def ParseDateRangeFromRequest(request):
    start, end = request.GET.get('dateStart'), request.GET.get('dateEnd')
    if start is None:
        return None, None

    try:
        start = datetime.strptime(start, "%Y-%m-%dT%H:%M:%S.%fZ")
        end = datetime.strptime(end, "%Y-%m-%dT%H:%M:%S.%fZ")
    except ValueError:
        raise ValidationError({
            'code': 400,
            'message': 'Wrong date format'
        })

    return start, end


def PutProductHistoryDataIntoDict(queryset):
    history = []
    for obj in queryset:
        obj_data = {
            'id': obj.product_id,
            'name': obj.name,
            'date': obj.date,
            'parentId': obj.parentId,
            'type': obj.type,
            'price': obj.price
        }
        history.append(obj_data)
    return history
