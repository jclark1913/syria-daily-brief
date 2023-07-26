class ScrapingError(Exception):
    """Custom exception class for errors during web scraping."""

    def __init__(self, message, url):
        super().__init__(message)
        self.url = url