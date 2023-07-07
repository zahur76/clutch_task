import scrapy
from scrapy import signals


import pymongo

myclient = pymongo.MongoClient(
    f"mongodb://zara:zara*2009@192.168.100.37:27017/?authMechanism=DEFAULT"
)

mydb = myclient["British_Dir"]


class QuotesSpider(scrapy.Spider):
    name = "british_dir"

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(QuotesSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signals.spider_closed)
        return spider

    def spider_closed(self, spider):
        print("end")

    def start_requests(self):
        for i in range(1, 1312):
            yield scrapy.Request(
                url=f"https://britishdir.co.uk/building-construction/page/{i}/",
                callback=self.parse_two,
            )

    def parse_two(self, response):
        links = response.css('p.more-link-wrap a::attr("href")').extract()

        for link in links:

            company_links = {
                'url': link,
                'complete': 0
            }

            mydb['british_dir_filters'].insert_one(company_links)

        # for link in links:
        #     yield scrapy.Request(
        #         url=response.urljoin(link),
        #         meta=dict(
        #             playwright=True,
        #             playwright_include_page=True,  # added
        #             errback=self.errback,  # added
        #         ),
        #     )

    # async def parse_three(self, response):
    #     print(response.url)
    #     page = response.meta["playwright_page"]  # playwright page meta data
    #     await page.close()  # close page after reques
    #     # print(response.url)
    #     try:
    #         # firm = response.css("div[itemprop='name'] strong::text").extract_first()

    #         # phone = response.css('a.phonelink::attr("href")').extract_first()

    #         # url = response.css(
    #         #     "a[itemprop='url']::attr('href')").extract_first()

    #         email = response.css("a[itemprop='email']::attr('href')").extract_first()

    #         print(email)

    #         # address = response.css("span.street::text").extract_first()

    #         # county = response.css("span.locality::text").extract_first()

    #         # postal = response.css("span.zip::text").extract_first()

    #         # country = response.css("span.country::text").extract_first()

    #         # if url and email:
    #         #     details = {
    #         #         "Source": "https://www.hotfrog.co.uk/",
    #         #         "Firm": firm,
    #         #         "URL": url,
    #         #         "Address Line 1": address,
    #         #         "Telephone Number": phone,
    #         #         "State Or County": county,
    #         #         "Postal Code": postal,
    #         #         'Country': country,
    #         #         "Business Sector 1": "Construction",
    #         #         "Email Address": email,
    #         #         "email_grabber": 1,
    #         #     }

    #         #     print(details)

    #         #     mydb["Construction"].insert_one(details)

    #         # elif url and not email:
    #         #     details = {
    #         #         "Source": "https://www.hotfrog.co.uk/",
    #         #         "Firm": firm,
    #         #         "URL": url,
    #         #         "Address Line 1": address,
    #         #         "Telephone Number": phone,
    #         #         "State Or County": county,
    #         #         "Postal Code": postal,
    #         #         'Country': country,
    #         #         "Business Sector 1": "Construction",
    #         #         "Email Address": None,
    #         #         "email_grabber": 0,
    #         #     }

    #         #     print(details)

    #         # mydb["Construction"].insert_one(details)

    #     except Exception as e:
    #         print(f"{e}")

    # async def errback(self, failure):
    #     page = failure.request.meta["playwright_page"]
    #     await page.close()
