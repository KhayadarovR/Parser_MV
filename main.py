import requests
from pars_setting import cookies, headers
import os
import math

prod_ids = []
prod_names = []
prod_prices = []
prod_prices_sort = []


def parsing():
    """Получаем количество элементов, в категории"""
    category_id = '5433'
    params = {
        'categoryId': category_id,
        'offset': '96',
        'limit': '24',
    }

    if not os.path.exists('data'):
        os.mkdir('data')

    session = requests.Session()
    try:
        response = session.get(url='https://www.mvideo.ru/bff/products/listing', params=params, cookies=cookies, headers=headers).json()
    except requests.exceptions.TooManyRedirects:
        pass
    finally:
        response = session.get(url='https://www.mvideo.ru/bff/products/listing', params=params, cookies=cookies,
                               headers=headers).json()

    total_items = response.get('body').get('total')

    if total_items is None:
        return 'No items'

    """Получаем количество страниц"""
    pages_count = math.ceil(total_items/int(params['limit']))
    print(f'Total pages: {pages_count} | Total items: {total_items}')


    """Пробегаемся по каждой странице и получаем IDники товаров"""
    for i in range(pages_count):
        offset = 24*i
        params = {
            'categoryId': category_id,
            'offset': offset,
            'limit': '24',
        }
        response = session.get('https://www.mvideo.ru/bff/products/listing', params=params, cookies=cookies,
                         headers=headers).json()
        prod_ids_list = response.get('body').get('products')
        for item in prod_ids_list:
            prod_ids.append(item)

        '''Получаем имена'''
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
            prod_names.append(descrip['name'])

        '''Получаем цены'''
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
            dir = {'id': item['productId'],
                   'price': item['price']['basePrice']}

            prod_prices.append(dir)

        print(str(i) + "-------------------------------")


def find_price():
    for j in range(len(prod_ids)):
        for item in prod_prices:
            if (item['id'] == prod_ids[j]):
                prod_prices_sort.append(item['price'])
                break


def printer():
    for i in range(len(prod_ids)):
        print(f'id: {prod_ids[i]} name: {prod_names[i]} price: {prod_prices_sort[i]} руб')


if __name__ == '__main__':
    parsing()
    find_price()
    printer()

