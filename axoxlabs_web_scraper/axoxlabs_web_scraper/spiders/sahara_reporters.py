import scrapy
import re


class SaharaReportersSpider(scrapy.Spider):

    name = "sahara_reporters"
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0'}

    def start_requests(self):
        """
        Yields list of categories URLs to scrape.
        """

        list_categories_mapping = [
            ("news", "article_type", "3A11"), ("politics", "article_topics", "3A12"), ("sports", "article_topics", "3A14"), ("entertainment", "article_topics", "3A15")]
        lists_urls = [
            "https://saharareporters.com/articles?f%5B0%5D={}%{}".format(item[1], item[2]) for item in list_categories_mapping]
        for url, category in zip(lists_urls, list_categories_mapping):
            yield scrapy.Request(
                url=url, headers=self.headers, meta={"category": category[0]}, callback=self.scrape_items)

    def scrape_items(self, response):

        number_pages_str = response.css(".pagination-next::attr(href)").extract()[-1].strip().replace(",", "").split("page=")[1]
        number_pages = int(number_pages_str)
        number_pages = 2  # Temporarily test 3 pages
        for page_num in range(number_pages+1):
            yield scrapy.Request(
                url="{}&page={}".format(response.url, str(page_num)),
                meta={"category": response.meta["category"]}, callback=self.scrape_page_items,
                dont_filter=True)

    def scrape_page_items(self, response):

        article_blocks = response.css(".views-element-container")[0].css(".card-content")
        for article in article_blocks[:1]:
            article_url = article.css("a::attr(href)").extract_first()
            yield scrapy.Request(
                url="{}{}".format("https://saharareporters.com/", article_url), meta={"category": response.meta["category"]}, callback=self.scrape_item)

    def scrape_item(self, response):

        headline = response.css("h1")[0].css("span::text").extract_first().strip()
        article_main_block = response.css(".node--type-article")[0]
        try:
            image_url = article_main_block.css(".group-header")[0].css("img::attr(src)").extract_first()
        except:
            image_url = ""
            pass

        posted_date = [item for item in article_main_block.css(".group-left").css("div::text").extract() if re.search("\d{4}", item)][0]

        if len(article_main_block.css(".group-left")[0].css("div"))>=5:
            author = article_main_block.css(".group-left")[0].css("div")[3].css("a::text").extract_first()
        else:
            author = ""

        paragraphs = article_main_block.css(".group-middle")[0].css("p::text").extract()
        description = " ".join(paragraphs)
        yield {
            'headline': headline,
            'image_url': image_url,
            'author': author,
            'posted_date': posted_date,
            'description': description,
            'newspaper_name': "Sahara Reporters",
            'category': response.meta["category"],
            'url': response.url
        }
