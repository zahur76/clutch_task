import scrapy
from scrapy import signals
from scrapy.selector import Selector

import pymongo

myclient = pymongo.MongoClient("mongodb://localhost:27017/")

mydb = myclient["helplinelaw"]

filter_collection_name = "filters_helplinelaw"

business_sector_1 = "Legal"

business_sector_2 = "Law Firms"

mycol = mydb["mywsba"]


class QuotesSpider(scrapy.Spider):
    name = "helplinelaw"

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(QuotesSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signals.spider_closed)
        return spider

    def spider_closed(self, spider):
        print("end")

    def start_requests(self):
        data_list = list(mydb[filter_collection_name].find({"complete": 0}))

        for data in data_list:
            yield scrapy.Request(
                url=data["url"],
                meta={"id": data["_id"]},
                callback=self.parse_one,
            )

    def parse_one(self, response):
        country = response.url.split("/")[-1].title().replace("%20", " ")

        state = None

        if "-" in country:
            state = country.split("-")[-1]
            country = country.split("-")[0]

        cities = response.css('.country_firms_city a::attr("href")').extract()

        for city in cities:
            yield scrapy.Request(
                url=response.urljoin(city),
                meta={"id": response.meta["id"], "country": country, "state": state},
                callback=self.parse_two,
            )

    def parse_two(self, response):
        city = response.url.split("/")[-1].title().replace("%20", " ")

        companies = response.css(
            '.country_category_lawyers > ul li > a::attr("href")'
        ).extract()

        for company in companies:
            yield scrapy.Request(
                url=response.urljoin(company),
                meta={
                    "id": response.meta["id"],
                    "country": response.meta["country"],
                    "state": response.meta["state"],
                    "city": city,
                },
                callback=self.parse_three,
            )

    def parse_three(self, response):
        try:
            firm = response.css("div.container h2::text").extract_first()

            name = response.css(
                "li:contains('Contact Person Name')::text"
            ).extract_first()

            url = response.css('a[id*="Website"]::attr("href")').extract_first()

            email = response.css(
                'img[src="/images/e-mail.png"] + a[href^="mailto"]::attr("href")'
            ).extract_first()

            address = (
                response.css("div.lawyerfirm_information ul li:nth-child(1)::text")
                .extract_first()
                .replace("\r", " ")
                .replace("\n", " ")
            )

            if not firm:
                firm = name

            if email:
                details = {
                    "Source": "https://www.helplinelaw.com/",
                    "Firm": firm,
                    "URL": url,
                    "Name": name,
                    "Email Address": email,
                    "City": response.meta["city"],
                    "State Or County": response.meta["state"],
                    "Address Line 1": address,
                    "Country": response.meta["country"],
                    "Business Sector 1": business_sector_1,
                    "Business Sector 2": business_sector_2,
                    "email_grabber": 1,
                }

                print(details)
                mydb["helplinelaw"].insert_one(details)
                mydb[filter_collection_name].update_one(
                    {"_id": response.meta["id"]}, {"$set": {"complete": 1}}
                )

        except Exception as e:
            print(e)
