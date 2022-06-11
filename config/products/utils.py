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
