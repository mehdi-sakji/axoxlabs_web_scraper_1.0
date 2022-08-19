"""
https://www.legit.ng/ scraper.
"""

import scrapy


class LegitScraper(scrapy.Spider):
    """
    Spider for scraping https://www.legit.ng/ articles.
    """

    name = "legit_scraper"

    def start_requests(self):
        """
        Yields list of categories URLs to scrape.
        """

        # TODO add Selenium browser
