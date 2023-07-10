import globalscrape

import deirezzor24
import enabbeladi
import houranfreeleague
import sana
import suwayda24
import syriadirect

from models import db, Entry

SCRAPER_MAPPING = {
    1: deirezzor24.get_deirezzor24_data,
    2: enabbeladi.get_enabbeladi_data,
    3: houranfreeleague.get_hfl_data,
    4: sana.get_sana_data,
    5: suwayda24.get_suwayda24_data,
    6: syriadirect.get_syriadirect_data,
}

def run_selected_scrapers(selections, stop_timestamp, collection_id):
    """Controller function that takes an array of values corresponding to websites
    and a stop timestamp. The function will then call the correct scraper for
    each website and instruct it to grab data until the stop_timestamp is reached.

    TODO: Current no error handling is in place at all.
    """

    # Empty list to be populated with scraper functions
    selected_scrapers = []

    # Uses the map of scrapers to populate selected_scrapers w/ appropriate
    # functions
    for num in selections:
        selected_scrapers.append(SCRAPER_MAPPING.get(int(num), []))

    # Empty list to be populated with entries
    entries = []

    # Iterate through selections and run each scraper individually
    for scraper in selected_scrapers:
        print(f"Scraping data from {scraper}")
        articles = scraper(stop_timestamp=stop_timestamp)
        entries.extend(articles)

    # Add all our entries to db. TODO: Find a better home for this.
    add_entries_to_db(entries=entries, collection_id=collection_id)

    return entries

def add_entries_to_db(entries, collection_id):
    """Adds entries to local db"""

    for e in entries:
        current_entry = Entry(
            collection_id=collection_id,
            title=e.get('title', ''),
            link=e.get('link', ''),
            date_posted=e.get('date_posted', ''),
            full_text=e.get('full_text', ''),
            publication="TEST"
        )
        db.session.add(current_entry)

    db.session.commit()