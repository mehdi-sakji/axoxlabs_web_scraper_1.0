"""
dailypost.ng scraper.
"""

import scrapy


class DailyPostScraper(scrapy.Spider):
    """
    Spider for scraping dailypost.ng articles.
    """

    name = "dailypost_scraper"

    def start_requests(self):
        """
        Yields list of categories URLs to scrape.
        """

        # upper limit page counts, only for first execution, then just scan the n last pages
        # list_categories_pages = {
        #    "politics": 4000, "hot-news": 11800, "sport-news": 5000, "entertainment": 1200
        # }
        list_categories_pages = {
            "politics": 2, "hot-news": 2, "sport-news": 2, "entertainment": 2
        }
        categories_mapping = {
            "politics": "politics",
            "hot-news": "news", "sport-news": "sports", "entertainment": "entertainment"}
        lists_categories_pages_urls = [
            {"url": "https://dailypost.ng/{}/page/{}".format(item, i+1), "category": categories_mapping[item]}
            for item in list_categories_pages.keys() for i in range(list_categories_pages[item])]
        for url in lists_categories_pages_urls:
            yield scrapy.Request(
                url=url["url"], meta={"category": url["category"]}, callback=self.scrape_page)

    def scrape_page(self, response):

        article_blocks = response.css(".mvp-blog-story-wrap")
        for article in article_blocks:
            article_url = article.css("a::attr(href)").extract_first()
            yield scrapy.Request(
                url=article_url, meta={"category": response.meta["category"]}, callback=self.scrape_item)

    def scrape_item(self, response):

        headline = response.css(".mvp-post-title::text").extract_first()
        try:
            image_url = response.css("#mvp-post-feat-img")[0].css("img::attr(src)").extract_first()
        except:
            image_url = ""
            pass
        author = response.css(".author-name")[0].css("a::text").extract_first().strip()
        posted_date = response.css(".post-date::attr(datetime)").extract_first().strip()
        paragraphs = response.css("#mvp-content-main")[0].css("p::text").extract()
        description = " ".join(paragraphs)
        yield {
            'headline': headline,
            'image_url': image_url,
            'author': author,
            'posted_date': posted_date,
            'description': description,
            'newspaper_name': "DailyPost Newspaper",
            'category': response.meta["category"],
            'url': response.url
        }
