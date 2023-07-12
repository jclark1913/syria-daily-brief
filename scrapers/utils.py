import time
import datetime
import math

# Default headers for all requests
DEFAULT_HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

# Map of Arabic Latin months to their corresponding calendar number
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
    "ديسمبر": "12",
}

# Map of Arabic months (standard fusHa names) to their corresponding calendar number
ARABIC_STANDARD_MONTHS = {
    "كانون الثاني": "1",
    "شباط": "2",
    "آذار": "3",
    "نيسان": "4",
    "أيار": "5",
    "حزيران": "6",
    "تموز": "7",
    "آب": "8",
    "أيلول": "9",
    "تشرين الأول": "10",
    "تشرين الثاني": "11",
    "كانون الأول": "12",
}

ARABIC_TIME_UNITS = {
    "minute": {"arabic": ["دقيقة", "دقائق", "دقيقتين"], "value": 60},
    "hour": {"arabic": ["ساعة", "ساعات", "ساعتين"], "value": 3600},
    "day": {"arabic": ["يوم", "أيام", "يومين"], "value": 86400},
    "week": {"arabic": ["أسبوع", "أسابيع", "أسبوعين"], "value": 604800},
    "month": {"arabic": ["شهر", "أشهر", "شهرين"], "value": 2629743},
    "year": {"arabic": ["سنة", "سنوات", "سنين", "سنتين"], "value": 31556926},
}


def get_generic_timestamp(date):
    """Takes date input and converts it to Unix timestamp.

    NOTE: Assumes date is in dd-mm-YYYY format.
    """

    # Uses time and datetime libs to generate Unix timestamp
    return time.mktime(datetime.datetime.strptime(date, "%d-%m-%Y").timetuple())


def get_approx_timestamp_from_last_updated_AR(last_updated):
    """Converts Arabic phrase in description to approximate timestamp.

    Assuming current time is 6/20/23 9pm (1687309200):

    "5 ساعات ago" -> (1687291200)

    NOTE: Currently works with both Deir Ezzor 24 and Suwayda 24.
    """

    # get current date
    current_timestamp = math.floor(datetime.datetime.now().timestamp())

    # subtract total seconds from desc from current date to generate approx timestamp
    return current_timestamp - get_total_seconds_from_last_updated_AR(last_updated)


def get_total_seconds_from_last_updated_AR(last_updated):
    """Returns the total number of seconds from the posted before section of an
    article. Useful for generating a unix timestamp by subtracting result from
    current time.

    NOTE: Currently works with both Deir Ezzor 24 and Suwayda 24.

    examples:

    "5 ساعات ago" -> 18000 (3600 * 5)
    "8 سنوات ago" -> 252455408 (63113852 * 8)
    "دقيقتين ago" -> 120 (60 * 2)

    """

    # Return variable
    total_seconds = 0

    # Create array of Arabic unit + quantity (if present)
    arabic_posted = [
        remove_RLM_char_from_str(word)
        for word in last_updated.split()
        if word != "ago" and word != "منذ"
    ]

    # The word for "one" in Arabic (minus gender ending)
    arabic_one = "واحد"

    # Ascertains duration (Arabic) and number of units
    if len(arabic_posted) == 1:
        duration = arabic_posted[0]
        quantity = 2
    elif arabic_one in arabic_posted[1]:
        duration = arabic_posted[0]
        quantity = 1
    else:
        duration = arabic_posted[1]
        quantity = int(arabic_posted[0])

    # Generate # of seconds from Arabic time units dictionary
    for unit in ARABIC_TIME_UNITS:
        if duration in ARABIC_TIME_UNITS[unit]["arabic"]:
            total_seconds = ARABIC_TIME_UNITS[unit]["value"] * quantity

    return total_seconds


def remove_RLM_char_from_str(str):
    """Removes unicode 'RIGHT-TO-LEFT' character from a given string and returns
    it.
    """

    return str.replace("\u200f", "")
