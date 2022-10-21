import scrapy
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor

class VanguardSpider(scrapy.Spider):
    
    name = "vanguard"
    
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0'}

    def start_requests(self):

        categories_mapping = {
            "politics": "politics", "business": "business",
            "national-news": "news", "sports": "sports", "entertainment": "entertainment"}
        list_categories = categories_mapping.keys()
        lists_urls = [
            "https://www.vanguardngr.com/category/{}/".format(item) for item in list_categories]
        for url, category in zip(lists_urls, list_categories):
            yield scrapy.Request(
                url=url, meta={"category": category}, headers=self.headers, callback=self.scrape_items)
    
    """
    def set_user_agent(self, request, spider):
        request.headers['User-Agent'] = self.user_agent
        return request
    
    rules = (
        Rule(LinkExtractor(restrict_xpaths="//h1[@class='post-title']/a"), callback='parse_item', follow=True, process_request='set_user_agent'),
         Rule(LinkExtractor(restrict_xpaths="//h3[@class='entry-title']/a"), callback='parse_item', follow=True, process_request='set_user_agent')
    )
    """

    def scrape_items(self, response):

        number_pages = response.css(".page-numbers::text").extract()[-2].strip().replace(",", "")
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

        headline = response.css(".entry-title::text").extract_first().strip()
        div_content = response.css(".entry-content")[0]
        image_url = None
        image_urls = div_content.css("img::attr(src)").extract()
        if len(image_urls):
            image_url = image_urls[0]
        author = div_content.css(".strong::text")[0].extract_first().replace("By", "").strip()
        posted_date = response.css(".published::text").extract_first().strip()
        paragraphs = div_content.css("p::text").extract()[1:]
        description = " ".join(paragraphs)
        yield {
            'headline': headline,
            'image_url': image_url,
            'author': author,
            'posted_date': posted_date,
            'description': description,
            'newspaper_name': "Vanguard Newspaper",
            'category': response.meta["category"],
            'url': response.url
        }
