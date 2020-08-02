import logging

logger = logging.getLogger(__name__)


async def get_pictograms(facility_id):
    """

    :param facility_id:
    :return:
    """
    pictograms = dict()
    try:
        response = await fetch(
            url=DINING_FACILITY_INFORMATION_URL,
            method="POST",
            body=f"resources_id={facility_id}",
            headers=default_headers)
    except tornado.httpclient.HTTPError as http_err:
        print(http_err)
        return

    soup = bs4.BeautifulSoup(response.body, DEFAULT_PARSER)

    menu_pictograms = soup\
        .find("h4", text="Piktogramme")\
        .parent\
        .findNextSibling('div')
    for menu_pictogram in menu_pictograms.findChildren("div", recursive=False):
        menu_pictogram_image_src = menu_pictogram.img["src"]
        menu_pictogram_description = menu_pictogram.text.strip()
        pictograms[menu_pictogram_image_src] = menu_pictogram_description

    return pictograms
