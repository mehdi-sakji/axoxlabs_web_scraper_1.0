import scrapy

class TheGuardianSpider(scrapy.Spider):

    name = "the_guardian"
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0'}

    def start_requests(self):
        """
        Yields list of categories URLs to scrape.
        """

        categories_mapping = {
            "politics": "politics", "sport": "sports", "news/nigeria": "news", "news/world": "news"}
        lists_urls = [
            "https://guardian.ng/category/{}".format(item) for item in categories_mapping.keys()]
        for url, category in zip(lists_urls, categories_mapping.keys()):
            yield scrapy.Request(
                url=url, headers=self.headers, meta={"category": categories_mapping[category]}, callback=self.scrape_items)

    # TODO integrate pagination OR selenium OR API to load more articles
    def scrape_items(self, response):

        three_articles_block = response.css(".list-articles")
        for three in three_articles_block:
            article_blocks = response.css(".item")
            for article in article_blocks:
                article_url = article.css("a::attr(href)").extract_first()
                yield scrapy.Request(
                    url=article_url, meta={"category": response.meta["category"]}, callback=self.scrape_item)

    def scrape_item(self, response):
        article_header = response.css(".article-header")[0]
        headline = article-header.css(".title::text").extract_first()
        try:
            image_url = article-header.css("img::attr(src)").extract_first()
        except:
            # No image
            image_url = ""
            pass
        author = response.css(".author")[0].css("strong::text").extract_first().strip()
        posted_date = response.css(".date::text").extract_first().strip()
        paragraphs = response.css(".single-article")[0].css("p::text").extract()
        description = " ".join(paragraphs)
        yield {
            'headline': headline,
            'image_url': image_url,
            'author': author,
            'posted_date': posted_date,
            'description': description,
            'newspaper_name': "The Sun News Paper",
            'category': response.meta["category"],
            'url': response.url
        }
