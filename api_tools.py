from pprint import pprint
from typing import List

import requests

import math

from requests import Response

import urllib.parse as urlparse
from urllib.parse import urlencode

from secrets import YANDEX_API_KEY

API_KEY = YANDEX_API_KEY


class WorldPoint:
    def __init__(self):
        self.latitude, self.longitude = 0.0, 0.0
        self.curr_json = None

    def set_toponym(self, toponym):
        if isinstance(toponym, (tuple, list, WorldPoint)):
            toponym = f'{toponym[0]},{toponym[1]}'

        geocoder_params = {
            "apikey": API_KEY,
            "geocode": toponym,
            "format": "json"
        }

        self.curr_json = get_toponym_json(geocoder_params)
        toponym = self.curr_json["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        toponym_coodrinates = toponym["Point"]["pos"]
        # Долгота и широта:
        self.longitude, self.latitude = map(float, toponym_coodrinates.split(' '))

    def set_pos(self, longitude, latitude):  # Долгота и Широта
        self.latitude, self.longitude = latitude, longitude

    def __getitem__(self, item):
        if item == 0:
            return self.longitude
        elif item == 1:
            return self.latitude
        raise IndexError(item)

    def __setitem__(self, key, value):
        if key == 0:
            self.longitude = value
        elif key == 1:
            self.latitude = value


class Marker:
    STYLE_PM = 'pm'
    STYLE_PM2 = 'pm2'
    STYLE_FLAG = 'flag'
    STYLE_VK = 'vk'
    STYLE_ORG = 'org'
    STYLE_HOME = 'home'
    STYLE_WORK = 'work'
    STYLE_YANDEX = 'ya_ru'
    ALL_STYLES = [STYLE_PM, STYLE_PM2, STYLE_FLAG, STYLE_VK, STYLE_ORG, STYLE_HOME, STYLE_WORK, STYLE_YANDEX]

    COLOR_WHITE = 'wt'
    COLOR_DARK_ORAGNE = 'do'
    COLOR_DARK_BLUE = 'db'
    COLOR_BLUE = 'bl'
    COLOR_GREEN = 'gn'
    COLOR_GRAY = 'gr'
    COLOR_LIGHT_BLUE = 'lb'
    COLOR_DARK_NIGHT = 'nt'
    COLOR_ORANGE = 'or'
    COLOR_PINK = 'pn'
    COLOR_RED = 'rd'
    COLOR_VIOLET = 'vv'
    COLOR_YELLOW = 'yw'
    COLOR_LETTER_A = 'a'
    COLOR_LETTER_B = 'b'
    COLOR_ORG = 'org'
    COLOR_DIR = 'dir'
    COLOR_BLUW = 'blyw'
    COLOR_BLACK = 'bk'
    COLOR_DARK_GREEN = 'dg'

    SIZE_BIG = 'l'
    SIZE_MEDIUM = 'm'
    SIZE_SMALL = 's'

    PM_COLOR_SUPPORT = [
        COLOR_WHITE, COLOR_DARK_ORAGNE, COLOR_DARK_BLUE,
        COLOR_BLUE, COLOR_GREEN, COLOR_GRAY, COLOR_LIGHT_BLUE,
        COLOR_DARK_NIGHT, COLOR_ORANGE, COLOR_PINK, COLOR_RED,
        COLOR_VIOLET, COLOR_YELLOW, COLOR_LETTER_A, COLOR_LETTER_B
    ]
    PM_SIZE_SUPPORT = [SIZE_SMALL, SIZE_MEDIUM, SIZE_BIG]

    PM2_COLOR_SUPPORT = [
        COLOR_WHITE, COLOR_DARK_ORAGNE, COLOR_DARK_BLUE, COLOR_BLUE,
        COLOR_GREEN, COLOR_GRAY, COLOR_LIGHT_BLUE, COLOR_DARK_NIGHT,
        COLOR_ORANGE, COLOR_PINK, COLOR_RED, COLOR_VIOLET, COLOR_YELLOW,
        COLOR_LETTER_A, COLOR_LETTER_B, COLOR_ORG, COLOR_DIR, COLOR_BLUW,
        COLOR_DARK_GREEN
    ]
    PM2_SIZE_SUPPORT = [SIZE_MEDIUM, SIZE_BIG]
    PM2_NO_CONTENT = [COLOR_LETTER_A, COLOR_LETTER_B, COLOR_ORG, COLOR_DIR, COLOR_BLUW]

    VK_COLOR_SUPPORT = [COLOR_BLACK, COLOR_GRAY]

    def __init__(self, point, visual='pmwtm'):
        self.point = point
        self._visual = visual

    def set_visual(self, style, color='', size='', content=None):
        assert style in Marker.ALL_STYLES
        if style == Marker.STYLE_PM:
            assert color in Marker.PM_COLOR_SUPPORT
            assert size in Marker.PM_SIZE_SUPPORT
            self._visual = f'{style}{color}{size}'
            if content is not None:
                if size == Marker.SIZE_BIG:
                    assert 0 < content <= 100
                else:
                    assert 0 < content < 100
                self._visual += str(content)
        elif style == Marker.STYLE_PM2:
            assert color in Marker.PM2_COLOR_SUPPORT
            assert size in Marker.PM2_SIZE_SUPPORT
            self._visual = f'{style}{color}{size}'
            if content is not None:
                assert color not in Marker.PM2_NO_CONTENT
                assert 0 < content < 100
                self._visual = self._visual + str(content)
        elif style == Marker.STYLE_VK:
            assert color in Marker.VK_COLOR_SUPPORT
            self._visual = f'{style}{color}m'
        else:
            self._visual = style

    def __str__(self):
        return f'{self.point[0]},{self.point[1]},{self._visual}'


class StaticAPIImage:
    LAYER_MAP = 'map'

    def __init__(self):
        self.marks: List[Marker] = []

    def get_response(self, delta, layer, point=None) -> Response:
        map_api_server = "http://static-maps.yandex.ru/1.x/"
        params = self.get_params(delta, layer)
        if point is not None:
            params["ll"] = f'{point[0]},{point[1]}'
        return requests.get(map_api_server, params=params)

    def get_params(self, delta, layer):
        params = {
            "spn": f"{delta},{delta}",
            "l": layer,
        }
        if self.marks:
            params['pt'] = '~'.join(map(str, self.marks))
        return params

    def to_http(self, delta, layer, point=None):
        url = "http://static-maps.yandex.ru/1.x/"
        params = self.get_params(delta, layer)

        url_parts = list(urlparse.urlparse(url))
        query = dict(urlparse.parse_qsl(url_parts[4]))
        query.update(params)

        url_parts[4] = urlencode(query)

        return urlparse.urlunparse(url_parts)


def lonlat_distance(a, b):
    degree_to_meters_factor = 111 * 1000  # 111 километров в метрах
    a_lon, a_lat = a
    b_lon, b_lat = b

    # Берем среднюю по широте точку и считаем коэффициент для нее.
    radians_lattitude = math.radians((a_lat + b_lat) / 2.)
    lat_lon_factor = math.cos(radians_lattitude)

    # Вычисляем смещения в метрах по вертикали и горизонтали.
    dx = abs(a_lon - b_lon) * degree_to_meters_factor * lat_lon_factor
    dy = abs(a_lat - b_lat) * degree_to_meters_factor

    # Вычисляем расстояние между точками.
    distance = math.sqrt(dx * dx + dy * dy)

    return distance


def get_map_params(coords=None, size=0.005, l_type='map', flags=(), vertexes=()):
    # Собираем параметры для запроса к StaticMapsAPI:
    map_params = {
        "spn": f"{size},{size}",
        "l": l_type,
        'pt': '~'.join([f'{flag[0][0]},{flag[0][1]},{flag[1]}' for flag in flags]),
        'pl': ','.join([f"{p[0]},{p[1]}" for p in vertexes])
    }
    if coords is not None:
        map_params["ll"] = ",".join(coords)
    # print(map_params)
    return map_params


# Not working
def get_lenght(points):
    params = {
        "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
        'waypoints': '|'.join([f"{p[0]},{p[1]}" for p in points]),
    }
    print(params)

    geocoder_api_server = "https://api.routing.yandex.net/v1.0.0/route"

    response = requests.get(geocoder_api_server, params=params)

    assert response

    json_response = response.json()
    return json_response


def get_toponym_json(params):
    geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"

    response = requests.get(geocoder_api_server, params=params)

    assert response

    json_response = response.json()
    return json_response


def get_toponym(toponym_to_find):
    geocoder_params = {
        "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
        "geocode": toponym_to_find,
        "format": "json"
    }

    json_response = get_toponym_json(geocoder_params)
    toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
    toponym_coodrinates = toponym["Point"]["pos"]
    # Долгота и широта:
    return toponym_coodrinates.split(" ")


def get_area(toponym_to_find):
    coords = get_toponym(toponym_to_find)
    geocoder_params = {
        "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
        "geocode": f'{coords[0]},{coords[1]}',
        "format": "json",
        'kind': 'district'
    }

    json_response = get_toponym_json(geocoder_params)["response"]["GeoObjectCollection"]["featureMember"][0]

    # Долгота и широта:
    return json_response["GeoObject"]['metaDataProperty']['GeocoderMetaData']['text']


def get_chemestry_json(coords):
    search_api_server = "https://search-maps.yandex.ru/v1/"
    api_key = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"

    address_ll = ",".join(coords)

    search_params = {
        "apikey": api_key,
        "text": "аптека",
        "lang": "ru_RU",
        "ll": address_ll,
        "type": "biz"
    }

    response = requests.get(search_api_server, params=search_params)
    assert response

    json_response = response.json()
    return json_response


def parse_chemestry(org):
    # Получаем координаты ответа.
    point = org["geometry"]["coordinates"]
    try:
        everyday = org["properties"]['CompanyMetaData']['Hours']['Availabilities'][0]['Everyday']
    except KeyError:
        everyday = None
    if everyday is not None:
        if everyday:
            color = 'gn'
        else:
            color = 'bl'
    else:
        color = 'gr'
    mark = f'pm2{color}m'
    return point, mark


def get_nearest(coords, num):
    json_response = get_chemestry_json(coords)

    # Получаем первую найденную организацию.
    res = []
    for i, org in enumerate(json_response["features"]):
        if i >= num:
            break
        res.append(parse_chemestry(org))
    # Название организации.
    # org_name = organization["properties"]["CompanyMetaData"]["name"]
    # Адрес организации.
    # org_address = organization["properties"]["CompanyMetaData"]["address"]
    return res
