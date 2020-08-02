import datetime
import logging
import typing
import stwberlin_menus.exceptions as exceptions
from tornado.httpclient import AsyncHTTPClient, HTTPRequest

logger = logging.getLogger(__name__)

_http_client = AsyncHTTPClient()
_default_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'
}

async def fetch(url, method="POST", body="", headers=None):
    params = dict(
        url=url,
        method=method,
        body=body,
        headers=headers or _default_headers)
    logger.debug(f"Fetching {params}")
    response = await _http_client.fetch(
        HTTPRequest(**params))
    return response


def as_datetime(date):
    return datetime.datetime.combine(date, datetime.datetime.min.time())


def date_string(d):
    return f'{d.year}-{d.month}-{d.day}'


def to_type(_type, value, catch=ValueError):
    try:
        x = _type(value)
        return x
    except catch:
        return None

def to_int(s):
    return to_type(lambda x: abs(int(x)), s, catch=ValueError)

def str_to_date(s: typing.List[str]) -> datetime.date:
    datetime.datetime.strptime(s, '%Y-%m-%d').date()
    # return to_type(lambda x: , s, catch=ValueError)

def all_of_type(_type, container, raises=ValueError()):
    for c in container:
        if not isinstance(c, _type):
            raise raises


def facility_name_for_id(facilities, facility_id):
    for _name, _code in facilities.items():
        if facility_id == _code:
            return _name
    return "Unknown"


def facility_ids_for_name(facilities, facility_name):
    found = list()
    for _name, _code in facilities.items():
        if facility_name.lower() in _name.lower():
            found.append(_code)
    if len(found) < 1:
        raise exceptions.STWBerlinScrapeUnknownDiningFacilityException(
            f'Could not find facility matching name "{facility_name}". Skipping.')
    return found
