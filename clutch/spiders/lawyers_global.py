import scrapy
from scrapy import signals
from scrapy.selector import Selector

import pymongo

myclient = pymongo.MongoClient("mongodb://localhost:27017/")

mydb = myclient["layers_global"]

collection_name = "law_firms"

business_sector_1 = "Legal"

business_sector_2 = "Law Firms"

mycol = mydb[collection_name]

urls = ["https://www.thelawyersglobal.org/law-firms/continents"]


class QuotesSpider(scrapy.Spider):
    name = "lawyers_global"

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(QuotesSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signals.spider_closed)
        return spider

    def spider_closed(self, spider):
        print("end")

    def start_requests(self):
        yield scrapy.Request(
            url=urls[0],
            callback=self.parse_one,
        )

    def parse_one(self, response):
        print(response.url)
        area_links = response.css("a.h2::attr('href')").extract()

        print(len(area_links))

        for area in area_links:
            yield scrapy.Request(
                url=response.urljoin(area),
                callback=self.parse_two,
            )

    def parse_two(self, response):
        cards = response.css("div.card.px-0").extract()

        next_page = response.css('a[aria-label="Next"]::attr("href")').extract_first()

        if next_page:
            yield scrapy.Request(
                url=response.urljoin(next_page),
                callback=self.parse_two,
            )

        for card in cards:
            try:
                firm = (
                    Selector(text=card)
                    .css("a.card-title::text")
                    .extract_first()
                )

                url = (
                    Selector(text=card).css("a.card-link::attr('href')").extract_first()
                )

                city = (
                    Selector(text=card)
                    .css("a[data-hit-type='city name click']::text")
                    .extract_first()
                )

                country = (
                    Selector(text=card)
                    .css("a[data-hit-type='country name click']::text")
                    .extract_first()
                )

                if url:
                    details = {
                        "Source": "https://www.thelawyersglobal.org/",
                        "Firm": firm,
                        "URL": url,
                        "Email Address": None,
                        "City": city,
                        "Country": country,
                        "Business Sector 1": business_sector_1,
                        "Business Sector 2": business_sector_2,
                        "email_grabber": 0,
                    }

                    print(details)
                    mydb[collection_name].insert_one(details)
            except Exception as e:
                print(e)
