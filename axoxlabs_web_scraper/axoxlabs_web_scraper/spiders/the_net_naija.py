import scrapy

class NetNaijaSpider(scrapy.Spider):
    """
    Spider for scraping thenetnaija.net articles.
    """

    name = "net_naija"
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0'}
    categories_mapping = {
            "News": "news", "BBNaija 2022": "news", "Celebrity Gist":"news", "Social Media":"news", "World":"news",
            "Crime":"news", "Happenings":"news", "Governance":"news", "Education News": "news",
            "Sports": "sports", "Politics": "politics", "Health": "health", "Entertainment": "entertainment",
            "Gaming": "entertainment", "Jokes - Riddles": "entertainment", "Music": "entertainment",
            "Lyrics": "entertainment", "Events": "entertainment", "Business News": "business"
        }

    def start_requests(self):

        # > Exact page count
        n_pages = 4000
        for i in range(n_pages):
            url = "https://www.thenetnaija.net/posts/page/{}".format(str(i+1))
            yield scrapy.Request(
                url=url, headers=self.headers, callback=self.scrape_page)

    def scrape_page(self, response):

        article_blocks = response.css(".post-entries")[0].css(".post-one")
        for article in article_blocks:
            article_url = article.css("a::attr(href)").extract_first()
            yield scrapy.Request(
                url=article_url, callback=self.scrape_item)

    def scrape_item(self, response):

        headline = response.css(".page-h1::text").extract_first()
        post_meta = response.css(".post-meta")[0]
        article = response.css("article")[0]
        
        
        try:
            image_url = article.css("figure")[0].css("img::attr(src)").extract_first()
        except:
            image_url = None
            pass
        category = post_meta.css("span::text").extract()[0].strip()
        author = post_meta.css("span::text").extract()[2].strip()
        posted_date = post_meta.css("span::text").extract()[1].strip()
        paragraphs = article.css("p::text").extract()
        description = " ".join(paragraphs)
        yield {
            'headline': headline,
            'image_url': image_url,
            'author': author,
            'posted_date': posted_date,
            'description': description,
            'newspaper_name': "TheNetNaija Newspaper",
            'category': self.categories_mapping(category),
            'url': response.url
        }
