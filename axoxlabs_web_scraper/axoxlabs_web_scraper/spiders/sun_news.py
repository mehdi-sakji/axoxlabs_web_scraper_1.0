import scrapy


class SunnewsonlineSpider(scrapy.Spider):

    name = "sunnewsonline"
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0'}

    def start_requests(self):
        """
        Yields list of categories URLs to scrape.
        """

        list_categories = [
            "business", "politics", "sporting-sun", "entertainment"]
        lists_urls = [
            "https://www.sunnewsonline.com/category/{}/".format(item) for item in list_categories]
        for url, category in zip(lists_urls, list_categories):
            yield scrapy.Request(
                url=url, headers=self.headers, meta={"category": category}, callback=self.scrape_items)

    def scrape_items(self, response):

        number_pages = int(response.css(".page_number::text").extract()[-1].strip().replace(",", ""))
        number_pages = 2  # Temporarily test 2 pages
        for page_num in range(number_pages):
            yield scrapy.Request(
                url="{}/page/{}".format(response.url, str(page_num+1)),
                meta={"category": response.meta["category"]}, callback=self.scrape_page_items,
                dont_filter=True)

    def scrape_page_items(self, response):

        article_blocks = response.css(".jeg_inner_content")[0].css("article")
        for article in article_blocks:
            article_url = article.css("a::attr(href)").extract_first()
            yield scrapy.Request(
                url=article_url, meta={"category": response.meta["category"]}, callback=self.scrape_item)

    def scrape_item(self, response):

        headline = response.css(".jeg_post_title::text").extract_first()
        try:
            image_url = response.css(".featured_image")[0].css("a::attr(href)").extract_first()
        except:
            image_url = ""
            pass
        author = response.css(".jeg_author_name::text").extract_first().strip()
        posted_date = response.css(".jeg_meta_date")[0].css("a::text").extract_first().strip()
        paragraphs = response.css(".content-inner")[0].css("p::text").extract()
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
