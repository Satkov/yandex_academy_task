from uuid import UUID


def get_request(context):
    """
    Проверяет, есть ли контекст в request
    """
    try:
        request = context.get('request')
    except KeyError:
        raise KeyError({
            'error': 'request was not received'
        })
    return request


def is_valid_uuid4(uuid_to_test):
    """
    Проверяет, валиден ли UUID
    """

    try:
        uuid_obj = UUID(uuid_to_test)
    except ValueError:
        return False
    except TypeError:
        return False
    return str(uuid_obj) == uuid_to_test


def SplitCategoryFromOffers(request_data):
    CATEGORIES = []
    OFFERS = []
    for obj_data in request_data:
        if obj_data.get('type') == 'CATEGORY':
            CATEGORIES.append(obj_data)
        else:
            OFFERS.append(obj_data)

    return CATEGORIES, OFFERS
