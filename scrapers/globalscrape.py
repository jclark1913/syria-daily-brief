import time
import datetime

# Global variables to assist with scraping

DEFAULT_HEADERS = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
}

ARABIC_LATIN_MONTHS = {
    "يناير": "1",
    "فبراير": "2",
    "مارس": "3",
    "أبريل": "4",
    "مايو": "5",
    "يونيو": "6",
    "يوليو": "7",
    "أغسطس": "8",
    "سبتمبر": "9",
    "أكتوبر": "10",
    "نوفمبر": "11",
    "ديسمبر": "12"
}

ARABIC_TIME_UNITS = {
    "minute": {"arabic": ["دقيقة", "دقائق", "دقيقتين"],
                "value": 60},
    "hour": {"arabic": ["ساعة", "ساعات", "ساعتين"],
                "value": 3600},
    "day": {"arabic": ["يوم", "أيام", "يومين"],
            "value": 86400},
    "week": {"arabic": ["أسبوع", "أسابيع", "أسبوعين"],
                "value": 604800},
    "month": {"arabic": ["شهر", "أشهر", "شهرين"],
                "value": 2629743},
    "year": {"arabic": ["سنة", "سنوات", "سنين", "سنتين"],
                "value": 31556926},
}

def get_generic_timestamp(date):
    """Takes date input and converts it to Unix timestamp.

    NOTE: Assumes date is in dd-mm-YYYY format.
    """

    # Uses time and datetime libs to generate Unix timestamp
    return time.mktime(datetime.datetime.strptime(date, "%d-%m-%Y").timetuple())