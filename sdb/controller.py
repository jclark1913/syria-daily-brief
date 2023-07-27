import os

print(os.getcwd())

from sdb.scrapers import (
    dez24,
    enabbaladi,
    houranfl,
    sana,
    suwayda24,
    syriadirect,
)

from sdb.models import db, Entry

from enum import Enum


class ScraperMap(Enum):
    DEZ24 = dez24.DEZ24
    ENABBALADI = enabbaladi.EnabBaladi
    HOURANFL = houranfl.HouranFL
    SANA = sana.SANA
    SUWAYDA24 = suwayda24.Suwayda24
    SYRIADIRECT = syriadirect.SyriaDirect


def run_selected_scrapers(selections, stop_timestamp, collection_id):
    """Controller function that takes an array of values corresponding to websites
    and a stop timestamp. The function will then call the correct scraper for
    each website and instruct it to grab data until the stop_timestamp is reached.
    """

    # List of dataclass objects to be returned
    all_data = []

    # Empty list to be populated with entries
    entries = []

    # Empty list for errors
    errors = []

    # Iterate through selections and run each scraper individually
    for scraper in selections:
        scraper = scraper.value()
        print(f"Gathering data from {scraper.publication}")
        data = scraper.get_data(stop_timestamp=stop_timestamp)
        entries += data.article_list

        # We will save the dataclass object for each scraper in a list for reference
        all_data.append(data)

        # If scraper was unsuccessful, we should get errors as well
        if not data.success:
            errors.append(data.error_message)

    # Add all our entries to db.
    add_entries_to_db(entries=entries, collection_id=collection_id)

    return all_data, errors


def add_entries_to_db(entries, collection_id):
    """Adds entries to local db"""

    for e in entries:
        current_entry = Entry(
            collection_id=collection_id,
            title=e.get("title", ""),
            link=e.get("link", ""),
            date_posted=e.get("date_posted", ""),
            full_text=e.get("full_text", ""),
            publication=e.get("publication", ""),
        )
        db.session.add(current_entry)

    db.session.commit()
