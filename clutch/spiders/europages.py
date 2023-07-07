import scrapy
from scrapy import signals


import pymongo

myclient = pymongo.MongoClient("mongodb://localhost:27017/")

mydb = myclient["europages"]

collection_name = "Beauty"

business_sector = "Beauty"

mycol = mydb[collection_name]

urls = [
    "https://www.europages.co.uk/companies/united%20kingdom/finance.html"
]

company_list = []

company_details = []

count = []


def find_between(s, first, last):
    try:
        start = s.index(first) + len(first)
        end = s.index(last, start)
        return s[start:end]
    except ValueError:
        return ""


class QuotesSpider(scrapy.Spider):
    name = "europages"

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(QuotesSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signals.spider_closed)
        return spider

    def spider_closed(self, spider):
        print("end")

    def start_requests(self):
        for url_ in urls:
            yield scrapy.Request(url=url_, callback=self.parse_one, meta={"URL": url_})

    def parse_one(self, response):
        country = response.url.split("/")[4].replace("%20", " ")
        category = response.url.split("/")[5].replace("%20", " ").replace(".html", "")

        company_links = response.css(
            "a.ep-ecard-serp__epage-link::attr('href')"
        ).extract()

        for company in company_links:
            yield scrapy.Request(
                url=response.urljoin(company),
                callback=self.parse_three,
                meta={"country": country, "category": category},
            )

        try:
            next_page = response.css(
                "a.ep-server-side-pagination-item::attr('href')"
            ).extract()
        except:
            next_page = None
        max_page = []
        for page in next_page:
            if "pg" in page:
                base_url = page
                number = find_between(page, "pg-", "/")
                max_page.append(int(number))

        # page_url = f"{base_url.split('/pg-')[0]}/pg-1/{base_url.split('/pg-')[1][1:]}"
        if next_page:
            for i in range(2, max(max_page) + 1):
                yield scrapy.Request(
                    url=response.urljoin(
                        f"{base_url.split('/pg-')[0]}/pg-{i}{base_url.split('/pg-')[1][1:]}"
                    ),
                    callback=self.parse_two,
                )

    def parse_two(self, response):
        country = response.url.split("/")[4].replace("%20", " ")
        category = response.url.split("/")[6].replace("%20", " ").replace(".html", "")

        company_links = response.css(
            "a.ep-ecard-serp__epage-link::attr('href')"
        ).extract()

        for company in company_links:
            yield scrapy.Request(
                url=response.urljoin(company),
                callback=self.parse_three,
                meta={"country": country, "category": category},
            )

    def parse_three(self, response):
        firm = response.css("h1.ep-epages-header-title::text").extract_first()

        url = response.css(
            "a.ep-epage-sidebar__website-button::attr('href')"
        ).extract_first()

        address = response.css("dl.ep-epages-sidebar__info p.ma-0::text").extract()

        city = response.css("dt:contains('Address') + dd p:nth-child(3)::text").extract_first().split(" ")[-1]


        if url:
            details = {
                "Source": "https://www.europages.co.uk",
                "Firm": firm.strip(),
                "URL": url,
                "City": city,
                "Country": response.meta["country"],
                "Address Line 1": " ".join(address).strip(),
                "Business Sector 1": response.meta["category"],
            }

            print(details)

            # mycol.insert_one(details)

        return
