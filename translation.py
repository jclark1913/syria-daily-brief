import argostranslate.package
import argostranslate.translate

from_code = "ar"
to_code = "en"

def initialize_argostranslate():
    """Should be run at the start of each scrape to update to latest language
    packs from Argos.
    """

    argostranslate.package.update_package_index()
    available_packages = argostranslate.package.get_available_packages()
    package_to_install = next(
        filter(
            lambda x: x.from_code == from_code and x.to_code == to_code,
            available_packages,
        )
    )
    argostranslate.package.install_from_path(package_to_install.download())

    return


def translate_ar_to_en(text):
    """Accepts Arabic text and returns it translated to English"""

    translated_text = argostranslate.translate.translate(text, from_code=from_code, to_code=to_code)
    return translated_text

def translate_given_entry(entry):
    """Translates a given entry and updates it in the db"""

    ar_title = entry.title
    ar_full_text = entry.full_text

    initialize_argostranslate()

    en_title = translate_ar_to_en(ar_title)
    en_full_text = translate_ar_to_en(ar_full_text)

    entry.title_translated = en_title
    entry.full_text_translated = en_full_text

    return



