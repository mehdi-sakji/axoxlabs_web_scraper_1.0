import scrapy

class TheNationSpider(scrapy.Spider):
    
    name = "the_nation"

    def start_requests(self):
        """
        Yields list of categories URLs to scrape.
        """

        # ~ exact page count
        # TODO fix exact or > exact number of pages
        list_categories_pages = {
           "news": 10000, "politics": 100, "business": 100, "sports": 100, "entertainment/entertainment-3": 100
        }
        # Page count for test
        list_categories_pages = {
            "news": 2, "politics": 2, "business": 2, "sports": 2, "entertainment/entertainment-3": 2
        }
        categories_mapping = {
            "news": "news", "politics": "politics", "business": "business", "sports": "sports",
            "entertainment/entertainment-3": "entertainment"}

        lists_categories_pages_urls = [
            {"url": "https://thenationonlineng.net/{}/page/{}/".format(item, i+1),
             "category": categories_mapping[item]}
            for item in list_categories_pages.keys() for i in range(list_categories_pages[item])]
        for url in lists_categories_pages_urls:
            yield scrapy.Request(
                url=url["url"], meta={"category": url["category"]}, callback=self.scrape_page)

    def scrape_page(self, response):

        # TODO handle embedded categories news --> politics (sports etc)
        article_blocks = response.css(".listing-blog")[0].css("article")
        for article in article_blocks:
            article_url = article.css(".title")[0].css("a::attr(href)").extract_first()
            yield scrapy.Request(
                url=article_url, meta={
                    "category": response.meta["category"]}, callback=self.scrape_item)

    @staticmethod
    def scrape_item(response):

        headline = response.css(".post-title::text").extract_first()
        try:
            image_url = response.css(".post-thumbnail")[0].css("img::attr(src)").extract_first()
        except:
            image_url = None
            pass
        author = response.css(".post-thumbnail")[0].css("img::attr(alt)").extract_first()
        posted_date = response.css(".post-published::attr(datetime)").extract_first().strip()
        paragraphs = response.css("entry-content")[0].css("p::text").extract()
        description = " ".join(paragraphs)
        yield {
            'headline': headline,
            'image_url': image_url,
            'author': author,
            'posted_date': posted_date,
            'description': description,
            'newspaper_name': "TheNation Newspaper",
            'category': response.meta["category"],
            'url': response.url
        }
