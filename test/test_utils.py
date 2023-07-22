from unittest import TestCase, mock
from syriadailybrief.scrapers.utils import (
    get_generic_timestamp,
    get_timestamp_from_arabic_latin_date,
    get_approx_timestamp_from_last_updated_AR,
    get_total_seconds_from_last_updated_AR,
    ARABIC_LATIN_MONTHS,
)

import datetime
import math


class UtilsTestCase(TestCase):
    """Tests for utils.py"""

    def test_get_generic_timestamp(self):
        """Does get_generic_timestamp return an accurate timestamp?"""

        generic_date = "01-01-2020"
        timestamp = get_generic_timestamp(generic_date)
        self.assertTrue(timestamp == 1577854800)

    def test_arabic_latin_months(self):
        """Does ARABIC_LATIN_MONTHS dictionary contain correct values?"""

        self.assertEqual(ARABIC_LATIN_MONTHS["يناير"], "1")
        self.assertEqual(ARABIC_LATIN_MONTHS["فبراير"], "2")
        self.assertEqual(ARABIC_LATIN_MONTHS["مارس"], "3")
        self.assertEqual(ARABIC_LATIN_MONTHS["أبريل"], "4")
        self.assertEqual(ARABIC_LATIN_MONTHS["مايو"], "5")
        self.assertEqual(ARABIC_LATIN_MONTHS["يونيو"], "6")
        self.assertEqual(ARABIC_LATIN_MONTHS["يوليو"], "7")
        self.assertEqual(ARABIC_LATIN_MONTHS["أغسطس"], "8")
        self.assertEqual(ARABIC_LATIN_MONTHS["سبتمبر"], "9")
        self.assertEqual(ARABIC_LATIN_MONTHS["أكتوبر"], "10")
        self.assertEqual(ARABIC_LATIN_MONTHS["نوفمبر"], "11")
        self.assertEqual(ARABIC_LATIN_MONTHS["ديسمبر"], "12")

    def test_get_timestamp_from_arabic_latin_date(self):
        """Does get_timestamp_from_arabic_latin_date return an accurate timestamp?"""

        arabic_latin_date1 = "يناير 01, 2020"
        timestamp1 = get_timestamp_from_arabic_latin_date(arabic_latin_date1)

        arabic_latin_date2 = "فبراير 15, 2023"
        timestamp2 = get_timestamp_from_arabic_latin_date(arabic_latin_date2)

        arabic_latin_date3 = "مارس 31, 2024"
        timestamp3 = get_timestamp_from_arabic_latin_date(arabic_latin_date3)

        self.assertTrue(timestamp1 == 1577854800)
        self.assertTrue(timestamp2 == 1676437200)
        self.assertTrue(timestamp3 == 1711857600)

    def test_get_total_seconds_from_last_updated_AR(self):
        """Does get_total_seconds_from_last_updated_AR return an accurate timestamp?"""

        last_updated_AR1 = "منذ 30 دقيقة"
        total_seconds1 = get_total_seconds_from_last_updated_AR(last_updated_AR1)

        last_updated_AR2 = "منذ سنتين"
        total_seconds2 = get_total_seconds_from_last_updated_AR(last_updated_AR2)

        last_updated_AR3 = "6 أشهر ago"
        total_seconds3 = get_total_seconds_from_last_updated_AR(last_updated_AR3)

        last_updated_AR4 = "‏يومين مضت"
        total_seconds4 = get_total_seconds_from_last_updated_AR(last_updated_AR4)

        self.assertTrue(total_seconds1 == 1800)
        self.assertTrue(total_seconds2 == 63113852)
        self.assertTrue(total_seconds3 == 15778458)
        self.assertTrue(total_seconds4 == 172800)

    def test_get_approx_timestamp_from_last_updated_AR(self):
        """Does get_approx_timestamp_from_last_updated_AR return an accurate timestamp?"""

        with mock.patch("math.floor", mock.Mock(return_value=1577854800)):
            """Mocking current time to 1/1/2020 12:00am"""

            self.assertEqual(
                math.floor(datetime.datetime.now().timestamp()), 1577854800
            )

            last_updated_AR1 = "منذ 30 دقيقة"
            timestamp1 = get_approx_timestamp_from_last_updated_AR(last_updated_AR1)

            last_updated_AR2 = "منذ سنتين"
            timestamp2 = get_approx_timestamp_from_last_updated_AR(last_updated_AR2)

            last_updated_AR3 = "6 أشهر ago"
            timestamp3 = get_approx_timestamp_from_last_updated_AR(last_updated_AR3)

            self.assertTrue(timestamp1 == 1577853000)
            self.assertTrue(timestamp2 == (1577854800 - 63113852))
            self.assertTrue(timestamp3 == (1577854800 - 15778458))


