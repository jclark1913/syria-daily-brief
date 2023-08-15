import os
import pandas as pd

from sdb.scrapers import (
    dez24,
    enabbaladi,
    houranfl,
    sana,
    suwayda24,
    syriadirect,
)

from sdb.models import db, Entry, Collection

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

    # Verify that collection exists before scraping starts
    try:
        Collection.query.get_or_404(collection_id)
    except Exception as e:
        raise Exception(f"Collection with id {collection_id} does not exist")

    # Iterate through selections and run each scraper individually
    for scraper in selections:
        scraper = scraper.value()
        print(f"Gathering data from {scraper.config.publication}")
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


def generate_excel_from_collection(collection_id):
    """Generates excel file from db"""

    # Get all entries from db
    entries = Entry.query.filter_by(collection_id=collection_id).all()

    # Create empty list to be populated with dicts
    entries_list = []

    # Iterate through entries and create dict for each
    for e in entries:
        current_entry = {
            "date_posted": e.date_posted,
            "publication": e.publication,
            "title": e.title,
            "title_translated": e.title_translated,
            "full_text": e.full_text,
            "full_text_translated": e.full_text_translated,
            "ai_summary": e.ai_summary,
            "link": e.link,
        }
        entries_list.append(current_entry)

    # Create dataframe from list of dicts
    df = pd.DataFrame(entries_list)

    # Create the directory if it doesn't exist
    os.makedirs("excels", exist_ok=True)

    # Get current timestamp and format as string
    current_timestamp = pd.Timestamp.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Create excel writer object
    writer = pd.ExcelWriter(
        f"../excels/output_collection{collection_id}_{current_timestamp}.xlsx"
    )

    # Write dataframe to excel
    df.to_excel(writer, index=False)

    # Save excel file
    writer.close()
