import scrapy
from scrapy import signals


import pymongo

myclient = pymongo.MongoClient("mongodb://localhost:27017/")

mydb = myclient["juriosity"]

collection_name = "legal"

business_sector_1 = "Legal"

business_sector_2 = "Law Firms"

mycol = mydb[collection_name]

urls = [
    "https://www.juriosity.com/directory/search?location=&page=500&q=&type=lawFirm"
]


class QuotesSpider(scrapy.Spider):
    name = "juriosity"

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(QuotesSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signals.spider_closed)
        return spider

    def spider_closed(self, spider):
        print("end")

    def start_requests(self):
        for i in range(1, 501):
            yield scrapy.Request(
                url=f"https://www.juriosity.com/directory/search?location=&page={i}&q=&type=lawFirm",
                callback=self.parse_one,
            )

    def parse_one(self, response):
        print(response.url)
        company_links = response.css(".__name a::attr('href')").extract()

        print(len(company_links))
        for company in company_links:
            yield scrapy.Request(
                url=response.urljoin(company),
                callback=self.parse_three,
            )

        # try:
        #     next_page = response.css(
        #         "a.page-link:contains('Next')::attr('href')"
        #     ).extract_first()
        # except:
        #     next_page = None

        # if next_page:
        #     yield scrapy.Request(
        #         url=response.urljoin(next_page),
        #         callback=self.parse_one,
        #     )

    def parse_two(self, response):
        print(response.url)
        try:
            name = response.css("h1.user-profile-masthead__name::text").extract_first()

            next_url = response.css(
                "div.user-profile-masthead__position-and-organisation a::attr('href')"
            ).extract_first()

            email = response.css(
                ".text-multiline a[href^='mailto']::attr('href')"
            ).extract_first()

            phone = response.css(
                    "dt:contains('Telephone') + dd a::attr('href')"
                ).extract_first()

            address = response.css('div.user-profile-masthead__address div::text').extract()
            print(address)
            if next_url:
                yield scrapy.Request(
                    url=response.urljoin(next_url),
                    meta={"Name": name, "name_email": email},
                    callback=self.parse_three,
                )
            print('------------------------------------')
            _details = {
                        "Source": "https://www.juriosity.com/",
                        "Firm": name,
                        "Name": name,
                        "URL": None,
                        "Email Address": email,
                        "City": address[0],
                        "Telephone Number": phone,
                        "Country": None,
                        "State Or County": address[1].split(',')[0],
                        "Address Line 1": " ".join(address).strip(),
                        "Business Sector 1": business_sector_1,
                        "Business Sector 2": business_sector_2,
                        "email_grabber": 1,
                    }

            print(_details)
            mycol.insert_one(_details)
        except Exception as e:
            print(e)
        
    def parse_three(self, response):

        try:
            firm = response.css(
                "h1.organisation-profile-masthead__name::text"
            ).extract_first()

            url = response.css(
                "dt:contains('Website') + dd a::attr('href')"
            ).extract_first()

            company_email = response.css(
                "dt:contains('Contact email') + dd a::attr('href')"
            ).extract_first()

            address = response.css("dt:contains('Address') + dd div::text").extract()

            city = response.css("dt:contains('Address') + dd div::text").extract()

            if len(city[-1]) == 1:
                city = city[-3]
            else:
                city = city[-2]

            print(city)

            state = response.css("div.organisation-profile-masthead__location::text").extract_first()

            phone = response.css(
                "dt:contains('Telephone') + dd a::attr('href')"
            ).extract_first()

            # _name = response.meta["Name"]
            # _email = response.meta["name_email"]

            # if _name and _email:
            #     print("Name present")
            #     _details = {
            #         "Source": "https://www.juriosity.com/",
            #         "Firm": firm,
            #         "Name": _name,
            #         "URL": url,
            #         "Email Address": company_email,
            #         "City": city,
            #         "Telephone Number": phone,
            #         "Country": None,
            #         "State Or County": state,
            #         "Address Line 1": " ".join(address).strip(),
            #         "Business Sector 1": business_sector_1,
            #         "Business Sector 2": business_sector_2,
            #         "email_grabber": 1,
            #     }

            #     print(_details)
            #     mycol.insert_one(_details)

            if company_email:
                details = {
                    "Source": "https://www.juriosity.com/",
                    "Firm": firm,
                    "URL": url,
                    "Email Address": company_email,
                    "City": city,
                    "Telephone Number": phone,
                    "Country": None,
                    "State Or County": state,
                    "Address Line 1": " ".join(address).strip(),
                    "Business Sector 1": business_sector_1,
                    "Business Sector 2": business_sector_2,
                    "email_grabber": 1,
                }
                print(details)
                mycol.insert_one(details)

            elif not company_email and url:
                details = {
                    "Source": "https://www.juriosity.com/",
                    "Firm": firm,
                    "URL": url,
                    "Email Address": company_email,
                    "City": city,
                    "Telephone Number": phone,
                    "Country": None,
                    "State Or County": state,
                    "Address Line 1": " ".join(address).strip(),
                    "Business Sector 1": business_sector_1,
                    "Business Sector 2": business_sector_2,
                    "email_grabber": 0,
                }
                print(details)

                mycol.insert_one(details)

        except Exception as e:
            print(e)
        return
