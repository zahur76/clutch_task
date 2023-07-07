import scrapy
from scrapy import signals
from scrapy.selector import Selector

import pymongo

myclient = pymongo.MongoClient(
    f"mongodb://zara:zara*2009@192.168.100.37:27017/?authMechanism=DEFAULT"
)

mydb = myclient["legal_500"]


class QuotesSpider(scrapy.Spider):
    name = "legal_500"

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(QuotesSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signals.spider_closed)
        return spider

    def spider_closed(self, spider):
        print("end")

    def start_requests(self):
        filters = mydb["legal_500_filters"].find({"complete": 0})

        for filter in filters:
            if filter["country"] == "united-kingdom-solicitors":
                _country = "United Kingdom"
            else:
                _country = filter["country"]
            yield scrapy.Request(
                url=filter["url"],
                meta={"Country": _country, "id": filter["_id"]},
                callback=self.parse_two,
            )

    def parse_two(self, response):
        firm_links = response.css("#directoryUL li a").extract()

        mydb["legal_500_filters"].update_one(
                {"_id": response.meta["id"]}, {"$set": {"complete": 1}}
            )

        for a in firm_links:
            city = Selector(text=a).css("::text").extract_first().split(" ")[0].strip()
            url = Selector(text=a).css("::attr('href')").extract_first()
            yield scrapy.Request(
                url=response.urljoin(url),
                meta={
                    "Country": response.meta["Country"],
                    "City": city,
                    "id": response.meta["id"],
                },
                callback=self.parse_three,
            )
        
    def parse_three(self, response):
        
        try:
            firm = (
                response.css('img[data-item-type="msd"]::attr("alt")')
                .extract_first()
                .split("company")[0]
            )

            url = response.css('a.firm-website::attr("href")').extract_first()

            email = response.css('a.firm-email::attr("href")').extract_first()

            address = response.css("div.address-box address::text").extract()

            if email:
                print("zaaazaaazzazaza")
                if "wales" in response.url.lower():
                    details = {
                        "Source": "https://www.legal500.com/",
                        "Firm": firm.strip(),
                        "Name": None,
                        "URL": url,
                        "Email Address": email,
                        "Country": response.meta["Country"],
                        "State Or County": "Wales",
                        "City": response.meta["City"].strip().replace("\t", ""),
                        "Address Line 1": " ".join(address).strip(),
                        "Business Sector 1": "Legal",
                        "Business Sector 2": "Law Firms",
                        "email_grabber": 1,
                    }

                    print(details)
                    mydb["legal_500_ALL"].insert_one(details)

                else:
                    details = {
                        "Source": "https://www.legal500.com/",
                        "Firm": firm.strip(),
                        "Name": None,
                        "URL": url,
                        "Email Address": email,
                        "Country": response.meta["Country"],
                        "State Or County": None,
                        "City": response.meta["City"].strip().replace("\t", ""),
                        "Address Line 1": " ".join(address).strip(),
                        "Business Sector 1": "Legal",
                        "Business Sector 2": "Law Firms",
                        "email_grabber": 1,
                    }

                    print(details)
                    mydb["legal_500_ALL"].insert_one(details)

            elif not email and url:
                print("aawweawewae")
                if "wales" in response.url.lower():
                    details = {
                        "Source": "https://www.legal500.com/",
                        "Firm": firm.strip(),
                        "Name": None,
                        "URL": url,
                        "Email Address": email,
                        "Country": response.meta["Country"],
                        "State Or County": "Wales",
                        "City": response.meta["City"].strip().replace("\t", ""),
                        "Address Line 1": " ".join(address).strip(),
                        "Business Sector 1": "Legal",
                        "Business Sector 2": "Law Firms",
                        "email_grabber": 0,
                    }
                    print(details)
                    mydb["legal_500_ALL"].insert_one(details)
                else:
                    details = {
                        "Source": "https://www.legal500.com/",
                        "Firm": firm.strip(),
                        "Name": None,
                        "URL": url,
                        "Email Address": email,
                        "Country": response.meta["Country"],
                        "State Or County": None,
                        "City": response.meta["City"].strip().replace("\t", ""),
                        "Address Line 1": " ".join(address).strip(),
                        "Business Sector 1": "Legal",
                        "Business Sector 2": "Law Firms",
                        "email_grabber": 1,
                    }

                    print(details)
                    mydb["legal_500_ALL"].insert_one(details)

            main_contacts = response.css("table.main-contacts tbody tr").extract()

            print(len(main_contacts))

            if main_contacts:
                for contact in main_contacts:
                    name = (
                        Selector(text=contact)
                        .css("td:nth-child(2)::text")
                        .extract_first()
                    )
                    person_email = (
                        Selector(text=contact).css('a::attr("href")').extract_first()
                    )
                    if person_email:
                        _details = {
                            "Source": "https://www.legal500.com/",
                            "Firm": firm.strip(),
                            "Name": name.strip(),
                            "URL": url,
                            "Email Address": person_email,
                            "Country": response.meta["Country"],
                            "State Or County": None,
                            "City": response.meta["City"].strip().replace("\t", ""),
                            "Address Line 1": " ".join(address).strip(),
                            "Business Sector 1": "Legal",
                            "Business Sector 2": "Law Firms",
                            "email_grabber": 1,
                        }
                        print(_details)
                        mydb["legal_500_ALL"].insert_one(_details)

        except Exception as e:
            print(e)
            
