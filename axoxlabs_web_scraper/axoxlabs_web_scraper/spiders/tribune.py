import scrapy

class TribuneSpider(scrapy.Spider):

    name = "tribune"
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0'}

    def start_requests(self):
        """
        Yields list of categories URLs to scrape.
        """

        list_categories = [
          "news", "health", "entertainment", "business"]
        # sports needs a specific spider
        lists_urls = [
            "https://tribuneonlineng.com/{}".format(item) for item in list_categories]
        for url, category in zip(lists_urls, list_categories):
            yield scrapy.Request(
                url=url, headers=self.headers, meta={"category": category}, callback=self.scrape_items)

    def scrape_items(self, response):

        article_blocks = response.css(".pt-cv-ifield")
        for article in article_blocks:
            article_url = article.css("a::attr(href)").extract_first()
            yield scrapy.Request(
                url=article_url, meta={"category": response.meta["category"]}, callback=self.scrape_item)

    def scrape_item(self, response):
        
        headline = response.css(".post_title::text").extract_first()
        try:
            image_url = response.css(".post-thumbnail::attr(href)").extract_first()
        except:
            # No image
            image_url = ""
            pass

        author = response.css(".post-author-name")[0].css("b::text").extract_first().strip()
        posted_date = response.css(".post-published")[0].css("b::text").extract_first().strip()
        paragraphs = response.css(".single-post-content")[0].css("p::text").extract()
        paragraphs = [item.strip() for item in paragraphs]
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
