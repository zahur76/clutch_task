import scrapy
from scrapy import signals


import pymongo

myclient = pymongo.MongoClient(
    "mongodb://zara:zara*2009@192.168.100.37:27017/?authMechanism=DEFAULT"
)

mydb = myclient["europages"]

collection_name = "Construction"

business_sector = "Construction"


class QuotesSpider(scrapy.Spider):
    name = "clutch_v2"

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(QuotesSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signals.spider_closed)
        return spider

    def spider_closed(self, spider):
        print("end")

    def start_requests(self):
        yield scrapy.Request(
            url=f"https://clutch.co/profile/smartsites#highlights",
            callback=self.parse_one,
        )

    def parse_one(self, response):
        print(response.url)
        company_links = response.css(
            "h1::text").extract_first()
        print(company_links)

    def parse_three(self, response):
        firm = response.css("h1.ep-epages-header-title::text").extract_first()

        url = response.css(
            "a.ep-epage-sidebar__website-button::attr('href')"
        ).extract_first()

        address = response.css("dl.ep-epages-sidebar__info p.ma-0::text").extract()

        city = (
            response.css("dt:contains('Address') + dd p:nth-child(3)::text")
            .extract_first()
            .split(" ")[-1]
        )

        if url:
            details = {
                "Source": "https://www.europages.co.uk",
                "Firm": firm.strip(),
                "URL": url,
                "City": city,
                "Country": country,
                "Address Line 1": " ".join(address).rstrip(),
                "Business Sector 1": "Construction",
            }

            print(details)

            # mycol.insert_one(details)

        return
