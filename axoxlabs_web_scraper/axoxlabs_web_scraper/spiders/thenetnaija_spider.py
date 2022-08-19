"""
https://www.thenetnaija.net/ scraper.
"""

import scrapy


class NetNaijaScraper(scrapy.Spider):
    """
    Spider for scraping thenetnaija.net articles.
    """

    name = "netnaija_scraper"

    def start_requests(self):
        """
        Yields list of categories URLs to scrape.
        """

        # Exact page count
        # list_categories_pages = {
        #    "posts": 3679, "videos": 864, "music": 750
        # }
        # >exact page count
        list_categories_pages = {
           "posts/news": 3500, "videos": 900, "music": 750
        }
        # Page count for test
        list_categories_pages = {
            "posts/news": 2, "videos": 2, "music": 2
        }
        categories_mapping = {
            "posts/news": "news", "videos": "entertainment", "music": "entertainment"}
        # TODO handle embedded categories news --> politics (sports etc)
        lists_categories_pages_urls = [
            {"url": "https://www.thenetnaija.net/{}/page/{}".format(item, i+1), "category": categories_mapping[item]}
            for item in list_categories_pages.keys() for i in range(list_categories_pages[item])]
        for url in lists_categories_pages_urls:
            yield scrapy.Request(
                url=url["url"], meta={"category": url["category"]}, callback=self.scrape_page)

    def scrape_page(self, response):

        # TODO handle embedded categories news --> politics (sports etc)
        article_blocks = response.css(".post-entries")[0].css(".post-one")
        for article in article_blocks:
            article_url = article.css("a::attr(href)").extract_first()
            yield scrapy.Request(
                url=article_url, meta={
                    "category": response.meta["category"]}, callback=self.scrape_item)

    @staticmethod
    def scrape_item(response):

        headline = response.css(".page-h1::text").extract_first()
        post_body = response.css(".post-body")[0]
        post_meta = response.css(".post-meta")[0]
        try:
            image_url = post_body.css("img::attr(src)").extract_first()
        except:
            image_url = None
            pass
        author = post_meta.css(".meta-one::text").extract()[2].strip()
        posted_date = post_meta.css(".meta-one::text").extract()[1].strip()
        paragraphs = post_body.css("p::text").extract()
        description = " ".join(paragraphs)
        yield {
            'headline': headline,
            'image_url': image_url,
            'author': author,
            'posted_date': posted_date,
            'description': description,
            'newspaper_name': "TheNetNaija Newspaper",
            'category': response.meta["category"],
            'url': response.url
        }
