import scrapy
from scrapy import signals
from scrapy.selector import Selector

import pymongo

myclient = pymongo.MongoClient("mongodb://localhost:27017/")

mydb = myclient["mywsba"]

filter_collection_name = "filter_mywsba"

business_sector_1 = "Legal"

business_sector_2 = "Lawyers"

mycol = mydb["mywsba"]

urls = [
    "https://www.mywsba.org/PersonifyEbusiness/LegalDirectory/LegalProfile.aspx?Usr_ID=000000043047"
]


class QuotesSpider(scrapy.Spider):
    name = "mywsba"

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(QuotesSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signals.spider_closed)
        return spider

    def spider_closed(self, spider):
        print("end")

    def start_requests(self):
        data_list = list(mydb[filter_collection_name].find({"complete": 0}).limit(40000))
        for data in data_list:
            yield scrapy.Request(
                url=data["url"],
                meta={"id": data["_id"]},
                callback=self.parse_one,
            )

    def parse_one(self, response):
        print(response.meta['id'])
        print(response.url)
        try:
            firm = response.css(
                'td:contains("Firm or Employer:") + td span::text'
            ).extract_first()

            name = response.css("span.name::text").extract_first()

            url = response.css('a[id*="Website"]::attr("href")').extract_first()

            email = response.css(
                'td:contains("Email:") + td span a::attr("href")'
            ).extract_first()

            address = response.css('span[id*="Address"]::text').extract()

            if not firm:
                firm = name

            if email:
                details = {
                    "Source": "https://www.mywsba.org/",
                    "Firm": firm,
                    "URL": url,
                    "Name": name,
                    "Email Address": email,
                    "City": None,
                    "State Or County": address[1].split(",")[0],
                    "Address Line 1": address[0],
                    "Address Line 2": address[1],
                    "Country": address[-1],
                    "Business Sector 1": business_sector_1,
                    "Business Sector 2": business_sector_2,
                    "email_grabber": 1,
                }

                print(details)
                mydb["mywsba"].insert_one(details)
                mydb[filter_collection_name].update_one(
                    {"_id": response.meta["id"]}, {"$set": {"complete": 1}}
                )

            elif url and not email:
                details = {
                    "Source": "https://www.mywsba.org/",
                    "Firm": firm,
                    "URL": url,
                    "Name": name,
                    "Email Address": None,
                    "City": None,
                    "State Or County": address[1].split(",")[0],
                    "Address Line 1": address[0],
                    "Address Line 2": address[1],
                    "Country": address[-1],
                    "Business Sector 1": business_sector_1,
                    "Business Sector 2": business_sector_2,
                    "email_grabber": 0,
                }

                print(details)
                mydb["mywsba"].insert_one(details)
                mydb[filter_collection_name].update_one(
                    {"_id": response.meta["id"]}, {"$set": {"complete": 1}}
                )

        except Exception as e:
            print(e)
