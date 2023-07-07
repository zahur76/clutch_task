"""                                                                      
Page Method Pagination example wAjax links
"""
import scrapy
from email_scraper import scrape_emails

import pymongo

# myclient = pymongo.MongoClient(
#     f"mongodb://zara:zara*2009@190.92.148.123:27017/?authMechanism=DEFAULT"
# )

myclient = pymongo.MongoClient(
    f"mongodb://zara:zara*2009@192.168.100.37:27017/?authMechanism=DEFAULT"
)

#mydb = myclient["soloedify"]
#mydb = myclient["Hotfrog"]
#mydb = myclient["europages"]
#mydb = myclient["lacartes"]
mydb = myclient["soloedify"]

campaign = "Health ROTW"


class QuotesSpider(scrapy.Spider):
    name = "email-grabber-retry"

    custom_settings = {
        'CONCURRENT_REQUESTS': 1
    }

    def start_requests(self):
        company_data = list(mydb[campaign].find({"email_grabber": 1, "Email Address": None}).limit(100))
        # company_data = list(mydb[campaign].find({"email_retry": 1}).limit(10000))

        print(len(company_data))

        for url in company_data:
            yield scrapy.Request(
                url["URL"],
                meta=dict(
                    id=url["_id"],
                ),
                callback=self.parse_one,
                errback=self.handle_error(url["_id"], url['URL']),
            )

    def parse_one(self, response):
        print(response.status)

        print(f'Response url: {response.meta["id"]}')

        email = response.css("a[href^='mailto']::attr('href')").extract_first()

        if email:
            print(email)
            mydb[campaign].update_one(
                {"_id": response.meta["id"]},
                {"$set": {"email_grabber": 1, "Email Address": email}},
            )

        else:
            print("no email detected USE: scrape_emails")

            scrape_email = scrape_emails(response.text)

            if scrape_email:
                for email_ in scrape_email:
                    print(f"Scrape emails: {email_}")
                    mydb[campaign].update_one(
                        {"_id": response.meta["id"]},
                        {"$set": {"email_grabber": 1, "Email Address": email_}},
                    )
                    break
                return
            else:
                contact = response.css('a[href*="/contact"]::attr("href")').extract_first()

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
                    return
                else:
                    print("contact page does not exist")
                    mydb[campaign].update_one(
                        {"_id": response.meta["id"]}, {"$set": {"email_grabber": 1, "email_retry": 0}}
                    )
                    return

    def parse_two(self, response):
        print("Contact page accessed")

        email = response.css("a[href^='mailto']::attr('href')").extract_first()

        print(email)

        print(f'Contact page: {response.meta["id"]}')


        if email:
            print(f"Email Obtained from Contact page: {email}")
            mydb[campaign].update_one(
                {"_id": response.meta["id"]},
                {"$set": {"email_grabber": 1, "Email Address": email}},
            )
            return
        else:
            print('No email on contact page')
            mydb[campaign].update_one(
                {"_id": response.meta["id"]}, {"$set": {"email_grabber": 1}}
            )
            return

    def handle_error(self, *arg):
        print(f"error: {arg[1]}")
        mydb[campaign].update_one({"_id": arg[0]}, {"$set": {"email_grabber": 1}})
