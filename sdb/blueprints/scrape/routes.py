from flask import Blueprint, jsonify, request

from multiprocessing import Process

from sdb.controller import get_available_scrapers, ScraperMap, run_selected_scrapers
from sdb.processes import cleanup_processes, ACTIVE_PROCESSES, STOP_EVENT
from sdb.schemas import ScrapeSchema

scrape = Blueprint("scrape", __name__)


@scrape.post("")
def scrape_data():
    """Initiates the scraping process.

    Accepts JSON:
    {
        selected_scrapers: [ENUMNAME, ...],
        stop_timestamp: int,
        collection_id: int
    }

    Returns: {message: "Scraping initiated."}
    """

    if "scraper" in ACTIVE_PROCESSES:
        return jsonify(error="Scraping already in progress."), 400

    # Resets the stop event
    STOP_EVENT.clear()

    # Gets JSON from request
    data = request.get_json()

    # Validate JSON schema
    scrape_schema = ScrapeSchema()
    scrape_schema.load(data)

    # Gets parameters from request
    scraper_strings = data["selected_scrapers"]
    stop_timestamp = data["stop_timestamp"]
    collection_id = data["collection_id"]

    # Gets enums corresponding to strings in scraper_strings
    try:
        selected_scrapers = [ScraperMap[scraper_str] for scraper_str in scraper_strings]
    except KeyError as e:
        raise Exception(f"Scraper {e} not found.")

    # Activates scraper and adds it to a process. When the process is finished it runs a cleanup.
    try:
        p = Process(
            target=run_selected_scrapers,
            args=(selected_scrapers, stop_timestamp, collection_id),
        )
        p.start()
        ACTIVE_PROCESSES["scraper"] = p
        p.join()
        if not STOP_EVENT.is_set():
            cleanup_processes()
    except Exception as e:
        return jsonify(error=str(e)), 400

    return jsonify({"message": "Scraping initiated."}), 200


@scrape.delete("")
def cancel_scrape():
    """Terminates any active scraping process.

    Returns (if success): {message: "Scraping terminated."}
    """

    # Is scraper currently running? If so, return error.
    if "scraper" not in ACTIVE_PROCESSES:
        return jsonify({"error": "Scraping is not currently in progress."}), 400

    # If scraper is running, terminate it by activating the stop event. Then, delete the process and clear the event.
    STOP_EVENT.set()
    ACTIVE_PROCESSES["scraper"].join()
    del ACTIVE_PROCESSES["scraper"]
    STOP_EVENT.clear()
    return jsonify({"message": "Scraping terminated."}), 200


@scrape.get("")
def get_scrapers():
    """Returns JSON containing names of available scrapers. This is used for selected scrapers and
    displaying publication names on the frontend..

    Returns:
        {[{value: ENUMNAME, label: "publication_name"}, ...]}
    }
    """

    available_scrapers = get_available_scrapers()

    return jsonify(available_scrapers)
