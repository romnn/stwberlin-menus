import re

DEFAULT_PARSER = "html.parser"
DEFAULT_HTTP_CLIENT = "simple_httpclient.AsyncHTTPClient"

DINING_FACILITY_CODES_URL =\
    "https://www.stw.berlin/mensen.html"
DINING_FACILITY_INFORMATION_URL =\
    "https://www.stw.berlin/xhr/speiseplan-und-standortdaten.html"
DINING_MENU_URL =\
    "https://www.stw.berlin/xhr/speiseplan-und-standortdaten.html"

xhr_load_matcher = re.compile(r"xhrLoad\('(\d+)'\)")
meal_price_matcher = re.compile(r"(\d+,\d+)")
meal_currency_matcher = re.compile(r"\$|€")
