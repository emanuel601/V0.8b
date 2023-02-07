import math
import requests
import numpy


ENDPOINT = 'https://api.mercadolibre.com/categories/MLA1744/attributes'
ENDPOINT_SEARCH = 'https://api.mercadolibre.com/sites/MLA/search?'  # este sirve para busquedas con ***

response = requests.get(url=ENDPOINT)
response.raise_for_status()

# year = input('ingrese anio (desde - hasta):\n')

auto = {}


def consult(offset, brand_name, model_name, brand, model, version, years):
    car_values = {
        "q": f"{brand_name} {model_name}",
        "MODEL": f"{model}",
        "BRAND": f"{brand}",
        "SHORT_VERSION": f"{version}",
        "VEHICLE_YEAR": f"{years}",
        'offset': offset,
        "limit": 50,
        "category_id": "MLA1744",

    }
    print(car_values)

    response_car_model = requests.get(url=ENDPOINT_SEARCH, params=car_values)
    response_car_model.raise_for_status()
    data = response_car_model.json()

    return data


def calc_price(brand_name, model_name, brand, model, version, years):
    data = consult(0, brand_name, model_name, brand, model, version, years)
    print(data['paging']['total'])

    if int(data['paging']['total']) <= 50:

        datos = data['results']
        price_list = [auto['price'] for auto in datos]

    else:
        datas = []
        price_list = []
        offset = 0
        pages = (data['paging']['total'])/50
        pages = math.ceil(pages)
        for page in range(pages):
            if page == 0:
                datas.append(data)
            else:
                offset += 50
                datas.append(consult(offset, brand_name, model_name, brand, model, version, years))

        print(len(datas))

        for x in datas:
            datos = x['results']
            for auto in datos:
                price_list.append(auto['price'])


    print(f'La longitud de la lista de precios sin filtar valores extremos es: {len(price_list)}')

    price_list = numpy.sort(price_list)

    elements = numpy.array(price_list)

    mean = numpy.mean(elements, axis=0)
    sd = numpy.std(elements, axis=0)

    final_list = [x for x in price_list if (x > mean - 2 * sd)]
    final_list = [x for x in final_list if (x < mean + 2 * sd)]

    print(f'el precio sugerido por una unidad de {brand_name} {model_name} {years} es: ${numpy.median(final_list)}')
    print(f'La longitud de la lista de precios sin valores extremos es: {len(final_list)}')
    price = numpy.median(final_list)
    num_cars = len(final_list)
    return price, num_cars
# calc_price()
