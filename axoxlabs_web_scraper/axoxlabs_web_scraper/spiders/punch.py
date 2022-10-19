"""
Punch spider.
"""

import scrapy


class PunchSpider(scrapy.Spider):

    name = "punch"
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0'}

    def start_requests(self):
        """
        Yields list of categories URLs to scrape.
        """

        list_categories = [
            "politics", "news", "sports", "entertainment", "business"]
        list_categories = list_categories[:3]  # Temporarily test 3 categories
        lists_urls = [
            "https://punchng.com/topics/{}".format(item) for item in list_categories]
        for url, category in zip(lists_urls, list_categories):
            yield scrapy.Request(
                url=url, headers=self.headers, meta={"category": category}, callback=self.scrape_items)

    def scrape_items(self, response):

        number_pages = response.css(".page-link::text").extract()[-2].strip().replace(",", "")
        number_pages = 2  # Temporarily test 2 pages
        for page_num in range(number_pages):
            yield scrapy.Request(
                url="{}/page/{}".format(response.url, str(page_num+1)),
                meta={"category": response.meta["category"]}, callback=self.scrape_page_items,
                dont_filter=True)

    def scrape_page_items(self, response):

        article_blocks = response.css("article")
        for article in article_blocks:
            article_url = article.css("a::attr(href)").extract_first()
            yield scrapy.Request(
                url=article_url, meta={"category": response.meta["category"]}, callback=self.scrape_item)

    @staticmethod
    def scrape_item(response):

        yield {
            'headline': response.xpath("////h1[@class='post-title']/text()").get(),
            'image_url': response.xpath("//div[@class='post-image-wrapper']/figure/img/@src").get(),
            'author': response.xpath(
                "(//span[@class='post-author']/strong)[1]/text()[normalize-space()]").get().strip(),
            'posted_date': response.xpath("//span[@class='post-date']/text()[normalize-space()]").get().strip(),
            'description': response.xpath("(//div[@class='post-content']/p)[1]/text()").get(),
            'newspaper_name': "Punch Newspaper",
            'category':  response.meta["category"],
            'url': response.url
        }
