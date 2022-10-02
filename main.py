import math
import requests
from pars_setting import cookies, headers

Products = []


def parsing(cat: int = 5431):
    """Парсер магазина mvideo.ru по категориям"""
    _category_id = str(cat)
    params = {
        'categoryId': _category_id,
        'offset': '96',
        'limit': '24',
    }
    session = requests.Session()
    try:
        response = session.get(url='https://www.mvideo.ru/bff/products/listing', params=params, cookies=cookies,
                               headers=headers).json()
    except requests.exceptions.TooManyRedirects:
        pass
    finally:
        response = session.get(url='https://www.mvideo.ru/bff/products/listing', params=params, cookies=cookies,
                               headers=headers).json()

    total_items = response.get('body').get('total')
    if total_items is None:
        return 'No items'

    # Get the number of pages
    pages_count = math.ceil(total_items / int(params['limit']))
    print(f'Total pages: {pages_count} | Total items: {total_items} in {cat}')

    for i in range(pages_count):
        # Get ids
        offset = 24 * i
        params = {
            'categoryId': cat,
            'offset': offset,
            'limit': '24',
        }
        response = session.get('https://www.mvideo.ru/bff/products/listing', params=params, cookies=cookies,
                               headers=headers).json()
        prod_ids_list = response.get('body').get('products')
        for item in prod_ids_list:
            Products.append({'id': item})

        # Get names
        json_data = {
            'productIds': prod_ids_list,
            'mediaTypes': [
                'images',
            ],
            'category': True,
            'status': True,
            'brand': True,
            'propertyTypes': [
                'KEY',
            ],
            'propertiesConfig': {
                'propertiesPortionSize': 5,
            },
            'multioffer': False,
        }
        response = session.post('https://www.mvideo.ru/bff/product-details/list', cookies=cookies, headers=headers,
                                json=json_data).json()
        prods = response.get('body').get('products')

        for descrip in prods:
            _id = descrip['productId']
            _name = descrip['name']
            for j in range(len(Products)):
                if _id == Products[j]['id']:
                    Products[j]['name'] = _name

        # Get price
        prod_ids_list_str = ','.join(prod_ids_list)
        params = {
            'productIds': prod_ids_list_str,
            'addBonusRubles': 'true',
            'isPromoApplied': 'true',
        }
        try:
            response = session.get('https://www.mvideo.ru/bff/products/prices', params=params, cookies=cookies,
                                   headers=headers).json()
        except requests.exceptions.TooManyRedirects:
            pass
        finally:
            response = session.get('https://www.mvideo.ru/bff/products/prices', params=params, cookies=cookies,
                                   headers=headers).json()

        prods = response.get('body').get('materialPrices')
        for item in prods:
            _id = item['productId']
            _price = item['price']['basePrice']
            for j in range(len(Products)):
                if _id == Products[j]['id']:
                    Products[j]['price'] = _price

        print(str(i) + " of " + str(pages_count) + " wait...")


def printer():
    for i in range(len(Products)):
        print(f'[{i}] {Products[i]["id"]} {Products[i]["name"]} \t {Products[i]["price"]} руб.')


if __name__ == '__main__':
    print(f'Start parse category')
    parsing(5431)
    printer()
    print('FINISH')
