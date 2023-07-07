import scrapy
from scrapy import signals
from scrapy.selector import Selector


start_urls = [
    'https://www.listofcompaniesin.com/france/cosmetics/'
    'https://www.listofcompaniesin.com/germany/cosmetics/',
    'https://www.listofcompaniesin.com/italy/cosmetics/',
    'https://www.listofcompaniesin.com/netherlands/cosmetics/',
    'https://www.listofcompaniesin.com/poland/cosmetics/',
    'https://www.listofcompaniesin.com/spain/cosmetics/',
    'https://www.listofcompaniesin.com/turkey/cosmetics/',
    'https://www.listofcompaniesin.com/ukraine/cosmetics/',
    'https://www.listofcompaniesin.com/united-kingdom/cosmetics/'
]


import pymongo

myclient = pymongo.MongoClient("mongodb://localhost:27017/")

mydb = myclient["LOC"]

mycol = mydb["results"]


class QuotesSpider(scrapy.Spider):
    name = "loc"

    custom_settings = {
        'CONCURRENT_REQUESTS': 1
    }

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(QuotesSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signals.spider_closed)
        return spider

    def spider_closed(self, spider):
        print('end')

    def start_requests(self):
        for url_ in start_urls:            
            yield scrapy.Request(url=url_, callback=self.parse_two)


    def parse_two(self, response):
    

        country = response.url.split('/')[3]
        company_links = response.css("h4 a::attr('href')").extract()

        print(len(company_links))

        for company_url in company_links:
            yield scrapy.Request(url=response.urljoin(company_url), meta={'Country': country}, callback=self.parse_three)

        next_ = response.css('a[title="Next"]::attr("href")').extract_first()

        if next_:
            yield scrapy.Request(url=response.urljoin(next_), callback=self.parse_two)

    def parse_three(self, response):

        try:
            firm =  response.css("h1::text").extract_first()

            url = response.css("a:contains('Visit website')::attr('href')").extract_first()

            name = response.css("strong:contains('Contact Person : ') + span::text").extract_first()

            phone = response.css("strong:contains('Telephone : ') + span::text").extract_first()

            address_1 = response.css("strong:contains('Location : ') + span::text").extract_first()

            sector_2 = response.css('li:nth-of-type(5) span a:nth-of-type(1)::text').extract_first()

            if url:
                details = {'Source': 'https://www.listofcompaniesin.com/', 'Firm': firm, 'URL': url, 'Name': name, 'Email Address': None, 'Phone NUmber': phone, 'Address Line 1': address_1,
                'Country': response.meta['Country'] , 'Business Sector 1': 'Cosmetics', 'Business Sector 2': sector_2, 'email_grabber': 0}
                
                print(details)

        
                mycol.insert_one(details)

        except Exception as e:
            print(e)

        
        return
