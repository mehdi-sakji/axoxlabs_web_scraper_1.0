import json

from flask import Flask
from scrapy.crawler import CrawlerProcess, CrawlerRunner
from twisted.internet import reactor
from scrapy.signalmanager import dispatcher
from scrapy import signals
from axoxlabs_web_scraper.spiders.punchung_spider import PunchungScraper

app = Flask(__name__)


@app.route('/')
def index():
    return 'Welcome to Punchung Scraper!'


@app.route('/scrape')
def scrape():

    results = []

    def crawler_results(signal, sender, item, response, spider):
        results.append(item)

    runner = CrawlerRunner()

    d = runner.crawl(PunchungScraper)
    d.addBoth(lambda _: reactor.stop())

    dispatcher.connect(crawler_results, signal=signals.item_scraped)

    reactor.run(installSignalHandlers=0)
    runner.stop()
    return json.dumps(results)


app.run(host='0.0.0.0', port=81)
