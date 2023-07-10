import globalscrape

import deirezzor24
import enabbeladi
import houranfreeleague
import sana
import suwayda24
import syriadirect

SCRAPER_MAPPING = {
    1: deirezzor24.get_deirezzor24_data,
    2: enabbeladi.get_enabbeladi_data,
    3: houranfreeleague.get_hfl_data,
    4: sana.get_sana_data,
    5: suwayda24.get_suwayda24_data,
    6: syriadirect.get_syriadirect_data,
}

def run_selected_scrapers(selections, stop_timestamp):
    """Controller function that takes an array of values corresponding to websites
    and a stop timestamp. The function will then call the correct scraper for
    each website and instruct it to grab data until the stop_timestamp is reached.
    """

    selected_scrapers = []

    for num in selections:
        selected_scrapers.append(SCRAPER_MAPPING.get(int(num), []))

    entries = []

    for scraper in selected_scrapers:
        print(f"Scraping data from {scraper}")
        articles = scraper(stop_timestamp=stop_timestamp)
        entries.extend(articles)

    return entries