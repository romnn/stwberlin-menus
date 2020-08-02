# -*- coding: utf-8 -*-

"""Console script for stwberlin_menus."""
import sys
import typing
import datetime
import logging
import progressbar
from pprint import pprint
import click
import time

import stwberlin_menus.utils as utils

# TODO: Replace these dependencies
import stwberlin_menus.getrid as utils2
import stwberlin_menus.getrid as asyncutils

from stwberlin_menus.codes import get_dining_facility_codes
from stwberlin_menus.menu import get_menu
from stwberlin_menus.codes import get_dining_facility_codes


def _parse_dates(ctx, param, values):
    bad_value_error = click.BadParameter("Dates must be valid dates with the format 2019-08-22.", ctx=ctx, param=param)
    missing_value_error = click.BadParameter("Need at least one valid date with the format 2019-08-22", ctx=ctx, param=param)
    if values is not None:
        parsed = [utils.to_date(d.strip()) for d in values if utils.to_date(d.strip()) is not None]
        if len(parsed) < 1:
            raise missing_value_error
        utils.all_of_type(datetime.date, parsed, raises=bad_value_error)
        if not len(parsed) == len(values):
            raise bad_value_error
        return parsed

def _parse_facility_ids(ctx, param, values):
    bad_value_error = click.BadParameter("Facility id's must be integers", ctx=ctx, param=param)
    if values is not None:
        parsed = [utils.to_int(_id.strip()) for _id in values if utils.to_int(_id.strip()) is not None]
        utils.all_of_type(int, parsed, raises=bad_value_error)
        if not len(parsed) == len(values):
            raise bad_value_error
        return parsed

def _parse_facility_names(ctx, param, values):
    bad_value_error = click.BadParameter("Facility names must be strings", ctx=ctx, param=param)
    print(values)
    if values is not None:
        parsed = [_name.strip() for _name in values if len(_name.strip()) > 0]
        utils.all_of_type(str, parsed, raises=bad_value_error)
        if not len(parsed) == len(values):
            raise bad_value_error
        return parsed



@click.command()
@click.option('--date', '-date', default=[utils.to_date(datetime.date.today())], callback=_parse_dates, multiple=True, help=(
            "The dates to scrape."
            "Can be a comma separated list, e.g. --dates='2019-08-22, 2019-08-23'"))
@click.option('--facility_id', '-id', default=[], callback=_parse_facility_ids, multiple=True, help=(
            "The numerical codes of the preferred dining facility to scrape"
            "Can be a comma separated list, e.g. --facility_ids='540, 657, 321'"
            "If not known, search with --facility_names"
            "Leave blank to scrape all facilities"))
@click.option('--facility_name', '-facility', '-name', default=[], callback=_parse_facility_names, multiple=True, help=(
            "The dining facilities names to scrape."
            "Queries facility id's and tries to match the names"
            "Leave blank to scrape all facilities"
            "Can be a comma separated list, e.g. --facility_names=''"))
def main(date, facility_id, facility_name) -> int:
    """Console script for stwberlin_menus."""

    dates = date or []
    facility_ids = facility_id or []
    facility_names = facility_name or []
    total_scrapes_necessary = (len(facility_names) + len(facility_ids)) * len(dates)

    assert len(dates) > 0, f"Must specify at least one valid date"

    progressbar.streams.wrap_stderr()
    logging.basicConfig()

    with progressbar.ProgressBar(
            max_value=total_scrapes_necessary + 1, redirect_stdout=True) as bar:
        scrape_interval = 1.0
        global progress
        progress = 0
        menus = list()

        print("Getting dining facility codes")
        codes = asyncutils.run_sync(get_dining_facility_codes)
        facilities = utils2.flatten(codes.values())
        if len(facility_ids) + len(facility_names) == 0:
            facility_ids = facilities.values()

        # Resolve all facility names
        for f_name in facility_names:
            facility_ids += utils.facility_ids_for_name(f_name)

        bar.max_value = len(facility_ids) + 1

        print(f"Scraping dates: {str(', ').join([utils.date_string(d) for d in dates])}")
        summary = (
                str(', ').join(facility_names)
                + ' (by name) '
                + str(', ').join([str(f) for f in facility_ids])
                + ' (by id) ')
        print(f"Scraping facilities: {summary}")
        print("\n" + "#" * 100 + "\n")

        def scrape_menu(facility_id, date):
            facility_name = utils.facility_name_for_id(facilities=facilities, facility_id=facility_id)
            print(f"Scraping facility {facility_name} with id #{f_id} on {utils.date_string(date)}")
            time.sleep(scrape_interval)
            menus.append(asyncutils.run_sync(
                get_menu, facility_id=facility_id, facility_name=facility_name, date=date))
            global progress
            progress += 1
            bar.update(progress)

        progress += 1
        bar.update(progress)

        for f_id in set(facility_ids):
            for date in dates:
                scrape_menu(facility_id=f_id, date=date)

        pprint(menus)

    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
