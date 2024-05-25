import scrapy
from scrapy import signals

import pymongo

# http://www.lacartes.com/business
myclient = pymongo.MongoClient(
    f"mongodb://zara:zara*2009@192.168.100.37:27017/?authMechanism=DEFAULT"
)

mydb = myclient["lacartes"]

mycol = mydb["legal"]

business_sector = "Finance"

# business_sector_2 = "Estate Lawyer"

urls = [
    "https://www.lacartes.com/search/w/businesses/c/Finance-Insurance/c2/Accountants-Book-Keeping",
    "https://www.lacartes.com/search/w/businesses/c/Finance-Insurance/c2/Banks",
    "https://www.lacartes.com/search/w/businesses/c/Finance-Insurance/c2/Cash-Advances",
    "https://www.lacartes.com/search/w/businesses/c/Finance-Insurance/c2/Consumer-Credit-Report",
    "https://www.lacartes.com/search/w/businesses/c/Finance-Insurance/c2/Credit-Finance-Companies",
    "https://www.lacartes.com/search/w/businesses/c/Finance-Insurance/c2/Debt-Adjusters",
    "https://www.lacartes.com/search/w/businesses/c/Finance-Insurance/c2/Debt-Counselling",
    "https://www.lacartes.com/search/w/businesses/c/Finance-Insurance/c2/Debt-Recovery-Services",
    "https://www.lacartes.com/search/w/businesses/c/Finance-Insurance/c2/Factoring-Brokers",
    "https://www.lacartes.com/search/w/businesses/c/Finance-Insurance/c2/Financial-Investment-Advice",
    "https://www.lacartes.com/search/w/businesses/c/Finance-Insurance/c2/Financial-Services",
    "https://www.lacartes.com/search/w/businesses/c/Finance-Insurance/c2/Foreign-Currency-Exchange",
    "https://www.lacartes.com/search/w/businesses/c/Finance-Insurance/c2/Insolvency-Practitioners",
    "https://www.lacartes.com/search/w/businesses/c/Finance-Insurance/c2/Insurance",
    "https://www.lacartes.com/search/w/businesses/c/Finance-Insurance/c2/Loans",
    "https://www.lacartes.com/search/w/businesses/c/Finance-Insurance/c2/Mortgage-Brokers",
    "https://www.lacartes.com/search/w/businesses/c/Finance-Insurance/c2/Pawn-Brokers",
    "https://www.lacartes.com/search/w/businesses/c/Finance-Insurance/c2/Payroll-Services",
    "https://www.lacartes.com/search/w/businesses/c/Finance-Insurance/c2/Prepaid-Stored-Value-Cards",
    "https://www.lacartes.com/search/w/businesses/c/Finance-Insurance/c2/Remittance-Services",
    "https://www.lacartes.com/search/w/businesses/c/Finance-Insurance/c2/Risk-Management",
    "https://www.lacartes.com/search/w/businesses/c/Finance-Insurance/c2/Security-Brokers-Dealers",
    "https://www.lacartes.com/search/w/businesses/c/Finance-Insurance/c2/Trade-Exchanges",
    "https://www.lacartes.com/search/w/businesses/c/Finance-Insurance/c2/Wealth-Management",
    "https://www.lacartes.com/search/w/businesses/c/Finance-Insurance/c2/Wire-Transfer-Money-Order",
]

class QuotesSpider(scrapy.Spider):
    name = "lacartes"

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(QuotesSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signals.spider_closed)
        return spider

    def spider_closed(self, spider):
        print("end")

    def start_requests(self):
        for link in urls:
            yield scrapy.Request(
                url=link,
                callback=self.parse_two,
            )

    def parse_two(self, response):


        business_sector_ = response.url.split("/")

        business_sector__ = None

        try:
            int(business_sector_[-1].replace('-', ' '))
            business_sector__ = business_sector_[-3].replace('-', ' ')
        except:
            business_sector__ = business_sector_[-1].replace('-', ' ')

        company_links = response.css('a.title::attr("href")').extract()

        for link in company_links:
            yield scrapy.Request(
                url=response.urljoin(link), callback=self.parse_three, meta={"Sector": business_sector__}
            )

        
        next_ = response.css('a.page-next::attr("href")').extract_first()

        if next_:
            print(next_)
            yield scrapy.Request(
                url=response.urljoin(next_), callback=self.parse_two
            )

    def parse_three(self, response):
        try:
            url = (
                response.css("div:contains('Website:') + div::text")
                .extract_first()
                .strip()
            )

            firm = response.css("div.page-title-inset h1::text").extract_first()

            try:
                phone = response.css("div:contains('Tel:') + div::text").extract_first()
            except Exception as e:
                print(e)
                phone = None

            address = response.css("div.r:nth-of-type(1) div.f::text").extract()
            if url:
                details = {
                    "Source": "https://www.lacartes.com/",
                    "Firm": firm,
                    "URL": url,
                    "Phone Number": phone,
                    "Address Line 1": " ".join(address).strip().replace("\n", ""),
                    "Business Sector 1": business_sector,
                    "Business Sector 2": response.meta["Sector"],
                    "Email Address": None,
                    "email_grabber": 0,
                }

            print(details)
            mycol.insert_one(details)

        except Exception as e:
            print(e)