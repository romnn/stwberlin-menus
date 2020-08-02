import logging
import stwberlin_menus.config as config
import stwberlin_menus.utils as utils
import stwberlin_menus.parsing as parsing
import stwberlin_menus.exceptions as exceptions
import stwberlin_menus.grpc.service_pb2 as models
import tornado.httpclient
import datetime
import bs4
import babel.numbers
from google.protobuf.timestamp_pb2 import Timestamp

logger = logging.getLogger(__name__)

def _pictogram_for(image_src, description):
    # Health indicators
    if "ampel_gruen" in image_src:
        return models.HealthPictogram(
            color="green",
            pictogram=models.Pictogram(
                emoji=":white_check_mark:",
                description="Die beste Wahl! Je öfter, desto besser!"
            ))
    elif "ampel_gelb" in image_src:
        return models.HealthPictogram(
            color="yellow",
            pictogram=models.Pictogram(
                emoji=":warning:",
                description="Eine gute Wahl! Immer mal wieder."
            ))
    elif "ampel_rot" in image_src:
        return models.HealthPictogram(
            color="red",
            pictogram=models.Pictogram(
                emoji=":no_entry:",
                description="Eher selten! Am Besten mit Grün kombinieren."
            ))
    # Pictograms
    elif "ohne Fisch- und Fleischzutaten" in description:
        return models.Pictogram(
            emoji=":blossom:",
            description="Vegetarisch")
    elif "veganen" in description:
        return models.Pictogram(
            emoji=":seedling:",
            description="Vegan")
    elif "Klimaessen" in description:
        return models.Pictogram(
            emoji=":earth_americas:",
            description="Klimaessen")
    elif "Fischerei" in image_src:
        return models.Pictogram(
            emoji=":fish:",
            description="Nachhaltige Fischerei")
    elif "nachhaltiger Erzeugung" in image_src:
        return models.Pictogram(
            emoji=":deciduous_tree:",
            description="Nachhaltige Erzeugung")
    # Unknown pictogram
    # Keep the description and use a default image
    return models.Pictogram(
        emoji=":grey_question:",
        description=description)


async def get_menu(facility_id, facility_name="Unknown", date=datetime.date.today(), locale=config.berlin_locale):
    """

    :param facility_id:
    :param facility_name:
    :param date:
    :param locale:
    :return:
    """
    day = date.isoweekday()
    pbdate = Timestamp().FromDatetime(utils.as_datetime(date))

    menu = dict()
    try:
        response = await utils.fetch(
                url=parsing.DINING_MENU_URL,
                method="POST",
                body=f"resources_id={facility_id}&date={date}")

    except tornado.httpclient.HTTPError as http_err:
        print(http_err)
        return

    # print(response.body)
    soup = bs4.BeautifulSoup(response.body, parsing.DEFAULT_PARSER)
    menu_content = soup.find("div", id="speiseplan")
    menu_legend = soup.find("div", id="legende")

    if not menu_legend:
        raise exceptions.STWBerlinScrapeUnknownDiningFacilityException()
    if not menu_content:
        raise exceptions.STWBerlinScrapeNoMenuException()

    # Get pictograms
    pictograms = dict()
    try:
        facility_pictograms = (menu_legend
            .find("h4", text="Piktogramme")
            .parent
            .findNextSibling('div'))
        for menu_pictogram in facility_pictograms.findChildren("div", recursive=False):
            menu_pictogram_image_src = menu_pictogram.img["src"]
            menu_pictogram_description = menu_pictogram.text.strip()
            pictograms[menu_pictogram_image_src] = menu_pictogram_description
    except AttributeError:
        logger.warning("No pictograms")
        pictograms = None

    # Get menu categories
    menu_categories = menu_content.findChildren("div", {"class": "splGroupWrapper"}, recursive=False)
    if (
            len(menu_categories) > 1
            or len(menu_categories) == 1 and "Kein Speisenangebot" not in "".join(
        [c.text for c in menu_categories])
    ):
        menu_category_name = "Unknown"
        for menu_category in menu_categories:
            for menu_category_meal in menu_category:
                if isinstance(menu_category_meal, bs4.NavigableString):
                    # Continue if not a tag
                    continue
                elif "splMeal" not in menu_category_meal.attrs.get("class", []):
                    # Create a new entry for the category
                    menu_category_name = menu_category_meal.div.text
                    menu[menu_category_name] = models.Meals()
                else:
                    # Query the meal's name
                    meal_name = menu_category_meal.span.text.strip()

                    # Query the meal's price and currency
                    _meal_prices_and_currency = menu_category_meal.find("div", {"class": "text-right"}).text.strip()
                    _meal_prices = parsing.meal_price_matcher.findall(_meal_prices_and_currency)
                    meal_currencies = parsing.meal_currency_matcher.findall(_meal_prices_and_currency)
                    meal_prices, meal_currency = [], config.berlin_currency

                    # Accept if some salad dressings do not have an explicit price
                    if (
                            len(_meal_prices) == 0
                            and menu_category_name.lower() == "salate"
                            and any(s in meal_name.lower() for s in ["dressing", "sauce"])
                    ):
                        meal_prices = [0.0]
                    else:
                        if not len(set(meal_currencies)) == 1:
                            raise ValueError("Multiple Currencies are currently not supported")
                        meal_currency = list(set(meal_currencies))[0]
                        for meal_price in _meal_prices:
                            try:
                                # Localize the price
                                meal_prices.append(
                                    float(babel.numbers.parse_decimal(meal_price, locale=locale)))
                            except (ValueError, babel.numbers.NumberFormatError):
                                pass

                    # Add the meal's allergens
                    meal_allergens = dict()
                    for meal_allergen_row in menu_category_meal.table.findChildren("tr", recursive=False):
                        row_entries = meal_allergen_row.findChildren("td", recursive=False)
                        allergen_code = row_entries[0].text.strip()
                        allergen = row_entries[1].text.strip()
                        meal_allergens[allergen_code] = allergen

                    # Add the meal's pictograms
                    meal_pictograms = list()
                    for meal_pictogram in menu_category_meal.findChildren("img"):
                        meal_pictogram_image_src = meal_pictogram["src"]
                        if meal_pictogram_image_src in pictograms.keys():
                            meal_pictogram_description = pictograms[meal_pictogram_image_src]
                            meal_pictograms.append(
                                _pictogram_for(image_src=meal_pictogram_image_src, description=meal_pictogram_description))
                                # models.MealPictogram.pictogram_for(
                                #     image_src=meal_pictogram_image_src,
                                #     description=meal_pictogram_description))

                    # Add the meal to the most recent category
                    print(dict(
                        facilityID=facility_id,
                        day=day,
                        date=pbdate,
                        description=meal_name,
                        category=menu_category_name,
                        prices=meal_prices,
                        currency=meal_currency,
                        allergens=meal_allergens,
                        pictograms=meal_pictograms
                    ))
                    meal = models.Meal(
                        facilityID=facility_id,
                        day=day,
                        date=pbdate,
                        description=meal_name,
                        category=menu_category_name,
                        prices=meal_prices,
                        currency=meal_currency,
                        allergens=meal_allergens,
                        pictograms=meal_pictograms
                    )
                    menu[menu_category_name].meals.append(meal)

    return models.MenuResult(
        facility=facility_id,
        facility_name=facility_name,
        day=day,
        date=pbdate,
        menu=menu
    )
