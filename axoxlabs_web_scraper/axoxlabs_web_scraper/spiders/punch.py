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
        lists_urls = [
            "https://punchng.com/topics/{}".format(item) for item in list_categories]
        for url, category in zip(lists_urls, list_categories):
            yield scrapy.Request(
                url=url, headers=self.headers, meta={"category": category}, callback=self.scrape_items)

    def scrape_items(self, response):

        number_pages = response.css(".page-link::text").extract()[-2].strip().replace(",", "")
        number_pages = 2  # TEMPORARILY FOR TEST
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
        
        headline = response.css(".post-title::text").extract_first().strip()
        try:
            image_url = response.css(".post-image-wrapper")[0].css("figure")[0].css("img::attr(src)").extract_first()
        except:
            image_url = ""
            pass
        
        author = response.css(".post-author")[0].css("a::text").extract_first().strip()
        posted_date = response.css(".post-date::text").extract_first().strip()
        paragraphs = response.css(".post-content")[0].css("p::text").extract()
        description = " ".join(paragraphs).strip()
        yield {
            'headline': headline,
            'image_url': image_url,
            'author': author,
            'posted_date': posted_date,
            'description': description,
            'newspaper_name': "Punch Newspaper",
            'category': response.meta["category"],
            'url': response.url
        }
        """
        yield {
            'headline': response.xpath("////h1[@class='post-title']/text()").get().strip(),
            'image_url': response.xpath("//div[@class='post-image-wrapper']/figure/img/@src").get(),
            'author': response.xpath(
                "(//span[@class='post-author'])[1]/text()[normalize-space()]").get().strip(),
            'posted_date': response.xpath("//span[@class='post-date']/text()[normalize-space()]").get().strip(),
            'description': response.xpath("(//div[@class='post-content']/p)[1]/text()").get(),
            'newspaper_name': "Punch Newspaper",
            'category':  response.meta["category"],
            'url': response.url
        }
        """
