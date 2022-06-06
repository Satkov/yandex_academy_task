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
