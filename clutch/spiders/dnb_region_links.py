import scrapy
from scrapy import signals


import pymongo

myclient = pymongo.MongoClient(
    f"mongodb://localhost:27017"
)

mydb = myclient["DNB"]

collection = "filters_finance"


class QuotesSpider(scrapy.Spider):
    name = "dnb_region_links"

    custom_settings = {
        'CONCURRENT_REQUESTS': 5
    }

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(QuotesSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signals.spider_closed)
        return spider

    def spider_closed(self, spider):
        print("end")

    def start_requests(self):
        countries = list(
                mydb[collection].find({"Complete": 0})
            )
        print(len(countries))
        for data in countries:
            yield scrapy.Request(
                url=data["url"],
                callback=self.parse_two,
            )

    def parse_two(self, response):
        print(response.url)
        