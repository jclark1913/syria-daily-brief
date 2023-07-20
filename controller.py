from scrapers import (
    dez24,
    enabbaladi,
    houranfl,
    sana,
    suwayda24,
    syriadirect,
)

from models import db, Entry

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

    TODO: Current no error handling is in place at all.
    """

    # Empty list to be populated with entries
    entries = []

    # Iterate through selections and run each scraper individually
    for scraper in selections:
        scraper = scraper.value()
        print(f"Gathering data from {scraper.publication}")
        articles = scraper.get_data(stop_timestamp=stop_timestamp)
        entries += articles

    # Add all our entries to db. TODO: Find a better home for this.
    add_entries_to_db(entries=entries, collection_id=collection_id)

    return entries


def add_entries_to_db(entries, collection_id):
    """Adds entries to local db"""

    for e in entries:
        current_entry = Entry(
            collection_id=collection_id,
            title=e.get("title", ""),
            link=e.get("link", ""),
            date_posted=e.get("date_posted", ""),
            full_text=e.get("full_text", ""),
            publication=e.get("publication", "")
        )
        db.session.add(current_entry)

    db.session.commit()
