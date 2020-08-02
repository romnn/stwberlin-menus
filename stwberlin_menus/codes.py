import logging
import stwberlin_menus.utils as utils
import stwberlin_menus.getrid as utils2
import stwberlin_menus.parsing as parsing
import tornado.httpclient
import bs4


logger = logging.getLogger(__name__)


async def get_dining_facility_codes():
    """

    :return:
    """
    dining_facilities = dict()
    try:
        response = await utils.fetch(
            url=parsing.DINING_FACILITY_CODES_URL,
            method="POST",
            body=""
        )
    except tornado.httpclient.HTTPError as http_err:
        print(http_err)
        return

    soup = bs4.BeautifulSoup(response.body, parsing.DEFAULT_PARSER)

    # Get all institutions that offer dining
    institutions = (
        soup
        .find("div", id="itemsHochschulen")
        .findChildren('div', recursive=False)
    )

    for institution in institutions:
        try:
            institution_name = institution.button.h4.text

            dining_facilities_of_institution = (institution
                .find('div', {'class': 'panel'})
                .findChildren('div', recursive=False))

            dining_facilities_for_institution = utils2.flatten([
                df.findChildren('div', recursive=False)
                for df in dining_facilities_of_institution])

            for dining_facility in dining_facilities_for_institution:
                dining_facility_name = dining_facility.find("a").text

                dining_facility_link = dining_facility.find(
                    lambda tag: "onclick" in tag.attrs.keys())

                dining_facility_id = int(
                    parsing.xhr_load_matcher.match(
                        dining_facility_link["onclick"]).group(1))

                if not dining_facilities.get(institution_name):
                    dining_facilities[institution_name] = dict()

                dining_facilities[institution_name][dining_facility_name] = dining_facility_id

        except Exception as e:
            raise e

    return dining_facilities
