"""
Page Method Pagination example wAjax links
"""
import scrapy
from scrapy import signals
from email_scraper import scrape_emails

import pymongo

myclient = pymongo.MongoClient(f"mongodb://zara:zara*2009@192.168.100.37:27017/?authMechanism=DEFAULT")

mydb = myclient["europages"]
# mydb = myclient["Hotfrog"]
# mydb = myclient["lacartes"]

campaign = "Construction"

filter_limit = 50000

retry = False

concurrent_request = 8


class QuotesSpider(scrapy.Spider):
    name = "email-grabber"
    custom_settings = {"CONCURRENT_REQUESTS": concurrent_request}

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(QuotesSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signals.spider_closed)
        return spider

    def spider_closed(self, spider):
        print("end")

    def start_requests(self):
        if not retry:
            company_data = list(
                mydb[campaign].find({"email_grabber": 0}).limit(filter_limit)
            )
        else:
            print("Executing Retry urls")
            company_data = list(mydb[campaign].find({"email_retry": 0}))
        print(f"{len(company_data)}: links obtained")
        for url in company_data:
            yield scrapy.Request(
                url["URL"],
                meta={"id": url["_id"], "Firm": url["Firm"]},
                callback=self.parse_one,
                errback=self.handle_error(url["_id"]),
            )

    def parse_one(self, response):
        print(response.status)

        print(f'Response url: {response.meta["id"]}')

        _firm = response.meta["Firm"]

        print(f"Response: {_firm}")

        if not _firm:
            _firm = response.css("title::text").extract_first()
            if _firm and "404" not in _firm:
                print(f"Firm name obtained: {_firm}")
                mydb[campaign].update_one(
                    {"_id": response.meta["id"]},
                    {"$set": {"Firm": _firm}},
                )

        email = response.css("a[href^='mailto']::attr('href')").extract_first()

        if email:
            print(email)
            if retry:
                mydb[campaign].update_one(
                    {"_id": response.meta["id"]},
                    {
                        "$set": {
                            "email_grabber": 1,
                            "Email Address": email,
                            "email_retry": 1,
                        }
                    },
                )
            else:
                mydb[campaign].update_one(
                    {"_id": response.meta["id"]},
                    {"$set": {"email_grabber": 1, "Email Address": email}},
                )

        else:
            print("no email detected USE: scrape_emails")

            scrape_email = scrape_emails(response.text)

            print(f"Scrape email list: {scrape_email}")

            if len(scrape_email) >= 1:
                for email_ in scrape_email:
                    print(f"Email obtained from scrape email: {email_}")
                    if retry:
                        mydb[campaign].update_one(
                            {"_id": response.meta["id"]},
                            {
                                "$set": {
                                    "email_grabber": 1,
                                    "Email Address": email,
                                    "email_retry": 1,
                                }
                            },
                        )
                    else:
                        mydb[campaign].update_one(
                            {"_id": response.meta["id"]},
                            {"$set": {"email_grabber": 1, "Email Address": email_}},
                        )
                    break
            else:
                try:
                    contact = response.css(
                        'a[href*="/contact"]::attr("href")'
                    ).extract_first()
                except Exception as e:
                    contact = None
                if contact:
                    print("contact page exists")
                    print(response.urljoin(contact))
                    yield scrapy.Request(
                        response.urljoin(contact),
                        meta=dict(
                            id=response.meta["id"],
                        ),
                        callback=self.parse_two,
                    )
                else:
                    print(f"add url:{response.url} to retry list")
                    mydb[campaign].update_one(
                        {"_id": response.meta["id"]},
                        {"$set": {"email_grabber": 1, "email_retry": 0}},
                    )

    def parse_two(self, response):
        print("Contact page accessed")

        email = response.css("a[href^='mailto']::attr('href')").extract_first()

        print(email)

        print(f'Contact page: {response.meta["id"]}')
        if email:
            print(f"Email Obtained from Contact page: {email}")
            if retry:
                mydb[campaign].update_one(
                    {"_id": response.meta["id"]},
                    {
                        "$set": {
                            "email_grabber": 1,
                            "Email Address": email,
                            "email_retry": 1,
                        }
                    },
                )
            else:
                mydb[campaign].update_one(
                    {"_id": response.meta["id"]},
                    {"$set": {"email_grabber": 1, "Email Address": email}},
                )
        return

    def handle_error(self, *arg):
        print("error")
        mydb[campaign].update_one({"_id": arg[0]}, {"$set": {"email_grabber": 1}})
