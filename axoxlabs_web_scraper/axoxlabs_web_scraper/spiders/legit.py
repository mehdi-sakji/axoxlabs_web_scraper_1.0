import scrapy

class LegitSpider(scrapy.Spider):

    name = "legit"
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0'}

    def start_requests(self):
        """
        Yields list of categories URLs to scrape.
        """

        categories_mapping = {
            "politics": "politics",
            
            "business-economy/technology": "business", "business-economy/money": "business",
            "business-economy/energy": "business", "business-economy/capital-market": "business",
            "business-economy/industry": "business", "business-economy/industry": "economy",
            
            "entertainment/celebrities": "entertainment", "entertainment/movies": "entertainment",
            "entertainment/music": "entertainment", "entertainment/tv-shows": "entertainment",
            "entertainment/gist": "entertainment", "entertainment/nollywood": "entertainment",
            "entertainment/fashion": "entertainment",
            
            "nigeria": "news", "world/europe": "news", "world/africa": "news", "world/us": "news"}
        
        # Sports need a custom spider
        lists_urls = [
            "https://www.legit.ng/{}".format(item) for item in categories_mapping.keys()]
        for url, category in zip(lists_urls, categories_mapping.keys()):
            yield scrapy.Request(
                url=url, headers=self.headers, meta={"category": categories_mapping[category]}, callback=self.scrape_items)

    # TODO integrate pagination OR selenium OR API to load more articles
    def scrape_items(self, response):

        header_articles_block = response.css(".l-taxonomy-page-hero__list")[0]
        header_articles_urls = [
            item.css("a::attr(href)").extract_first() for item in header_articles_block.css("article")]
        body_articles_block = response.css(".js-articles")[0]
        body_articles_urls = [
            item.css("a::attr(href)").extract_first() for item in body_articles_block.css("article")]
        
        for url in header_articles_urls + body_articles_urls:
            yield scrapy.Request(
                url=url, meta={"category": response.meta["category"]}, callback=self.scrape_item)

    def scrape_item(self, response):
        
        article_block = response.css(".js-article-body")[0]
        headline = article_block.css(".c-main-headline::text").extract_first()
        try:
            image_url = article_block.css(".article-image")[0].css("img::attr(src)").extract_first()
        except:
            # No image
            image_url = ""
            pass
        author = article_block.css(".post__info")[0].css(".c-article-info__author::text").extract_first().strip()
        posted_date = article_block.css(".post__info")[0].css(".c-article-info__time::text").extract_first().strip()
        
        paragraphs = article_block.css(".post__content")[0].css("p::text").extract()
        description = " ".join(paragraphs)
        yield {
            'headline': headline,
            'image_url': image_url,
            'author': author,
            'posted_date': posted_date,
            'description': description,
            'newspaper_name': "Legit NG",
            'category': response.meta["category"],
            'url': response.url
        }
