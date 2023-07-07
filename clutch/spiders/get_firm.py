"""
Page Method Pagination example wAjax links
"""
import scrapy
from scrapy import signals
from email_scraper import scrape_emails

import pymongo

myclient = pymongo.MongoClient(
    f"mongodb://zara:zara*2009@190.92.148.123:27017/?authMechanism=DEFAULT"
)

mydb = myclient["soleadify"]
# mydb = myclient["Hotfrog"]
# mydb = myclient["lacartes"]

campaign = "Fitness ROTW"

filter_limit = 5000

concurrent_request = 8


class QuotesSpider(scrapy.Spider):
    name = "firm-name"
    custom_settings = {"CONCURRENT_REQUESTS": concurrent_request}

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(QuotesSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signals.spider_closed)
        return spider

    def spider_closed(self, spider):
        print("end")

    def start_requests(self):
       
        company_data = list(
            mydb[campaign].find({"Firm": None}).limit(filter_limit)
        )

        print(len(company_data))

        for url in company_data:
            if url['URL']:
                yield scrapy.Request(
                    url["URL"],
                    meta={"id": url["_id"]},
                    callback=self.parse_one,
                    errback=self.handle_error(url["_id"]),
                )
        

    def parse_one(self, response):
        print(response.status)

        print(f'Response url: {response.meta["id"]}')

        firm_name = response.css("title::text").extract_first()

        print(firm_name)

        
    def handle_error(self, *arg):
        print("error")
        mydb[campaign].update_one({"_id": arg[0]}, {"$set": {"email_grabber": 1}})
