import scrapy

class NetNaijaSpider(scrapy.Spider):
    """
    Spider for scraping thenetnaija.net articles.
    """

    name = "net_naija"
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0'}

    def start_requests(self):
        """
        Yields list of categories URLs to scrape.
        """

        # > Exact page count
        n_pages = 4000
        
        categories_mapping = {
            "News": "news", "BBNaija 2022": "news", "Celebrity Gist":"news", "Social Media":"news", "World":"news",
        
        }
        # TODO handle embedded categories news --> politics (sports etc)
        lists_categories_pages_urls = [
            {"url": "https://www.thenetnaija.net/{}/page/{}".format(item, i+1), "category": categories_mapping[item]}
            for item in list_categories_pages.keys() for i in range(list_categories_pages[item])]
        for url in lists_categories_pages_urls:
            yield scrapy.Request(
                url=url["url"], headers=self.headers, meta={"category": url["category"]}, callback=self.scrape_page)

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
