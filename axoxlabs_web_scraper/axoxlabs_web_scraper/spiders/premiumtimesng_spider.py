"""
https://www.premiumtimesng.com/ scraper.
"""

import scrapy


class PremiumTimesScraper(scrapy.Spider):
    """
    Spider for scraping https://www.premiumtimesng.com/ articles.
    """

    name = "premium_times_scraper"

    def start_requests(self):
        """
        Yields list of categories URLs to scrape.
        """

        categories_mapping = {
            "news": "news", "business": "business", "sports": "sports"}
        list_categories = categories_mapping.keys()
        lists_urls = [
            "https://www.premiumtimesng.com/category/{}".format(item) for item in list_categories]
        for url, category in zip(lists_urls, list_categories):
            yield scrapy.Request(
                url=url, meta={"category": category}, callback=self.scrape_items)

    def scrape_items(self, response):

        number_pages = response.css(".page_number::text").extract()[-2].strip().replace(",", "").replace(".", "")
        number_pages = 2  # Temporarily test 2 pages
        for page_num in range(int(number_pages)):
            yield scrapy.Request(
                url="{}/page/{}".format(response.url, str(page_num+1)),
                meta={"category": response.meta["category"]}, callback=self.scrape_page_items,
                dont_filter=True)

    def scrape_page_items(self, response):

        article_blocks = response.css(".jeg_posts")[0].css(".jeg_post")
        for article in article_blocks:
            article_url = article.css(".jeg_post_title")[0].css("a::attr(href)").extract_first()
            yield scrapy.Request(
                url=article_url, meta={"category": response.meta["category"]}, callback=self.scrape_item)

    @staticmethod
    def scrape_item(response):

        headline = response.css(".entry-header")[0].css(
            ".jeg_post_title::text").extract_first().strip()
        image_urls = response.css(".jeg_featured")[0].css("img::attr(src)").extract()
        image_url = None
        if len(image_urls):
            image_url = image_urls[0]
        author = response.css(".jeg_meta_author")[0].css("a::text").extract_first().strip()
        posted_date = response.css(".jeg_meta_date")[0].css("a::text").extract_first().strip()
        paragraphs = response.css(".entry-content")[0].css("p::text").extract()
        description = " ".join(paragraphs)
        yield {
            'headline': headline,
            'image_url': image_url,
            'author': author,
            'posted_date': posted_date,
            'description': description,
            'newspaper_name': "Premium Times Ng Newspaper",
            'category': response.meta["category"],
            'url': response.url
        }
