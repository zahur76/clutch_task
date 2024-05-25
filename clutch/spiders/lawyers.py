import scrapy
from scrapy import signals
from scrapy.selector import Selector


start_urls = [
               'https://lawyers.findlaw.com/']


import pymongo

myclient = pymongo.MongoClient("mongodb://localhost:27017/")

mydb = myclient["findlaw"]

mycol = mydb["findlaw"]


class QuotesSpider(scrapy.Spider):
    name = "findlaw"

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
        state_links = response.css(".states-links a::attr('href')").extract()


        print(len(state_links))

        # for company_url in company_links:
        #     yield scrapy.Request(url=response.urljoin(company_url), callback=self.parse_three , dont_filter=True)

        # next_ = response.css('div.nextLink a::attr("href")').extract_first()

        # if next_:
        #     yield scrapy.Request(url=response.urljoin(next_), callback=self.parse_two , dont_filter=True)

    def parse_three(self, response):
        print(response.url)
        try:
            firm =  response.css("h1::text").extract_first()

            url = response.css("div[itemprop=url] a::attr('href')").extract_first()

            script_ = response.css("div.compInfoDetail script").extract_first()

            email_ = None
            
            if script_:

                script_ = script_.replace('<script>', '').replace('document.write(emrp(', '').replace(",'construction.co.uk'));</script>", '').replace("'",'')

                email_ = ''

                for letter in script_:
                    if letter == 'A':
                        email_ += '@'
                    else:
                        email_ += chr(ord(letter) - 1)
                print(email_)
    
            address_1 = response.css("div[itemprop=streetAddress]::text").extract_first()

            address_2 = response.css("div[itemprop=addressLocality]::text").extract_first()

            address_3 = response.css("div[itemprop=addressCountry]::text").extract_first()
            

            if email_:
                details = {'Source': 'https://www.construction.co.uk/', 'Firm': firm, 'URL': url, 'Email Address': email_, 'Address Line 1': address_1,
                'State Or County': address_2, 'Country': address_3 , 'Business Sector 1': 'Construction', 'Business Sector 2': 'Builders', 'email_grabber': 1}
            elif url and not email_:
                details = {'Source': 'https://www.construction.co.uk/', 'Firm': firm, 'URL': url, 'Email Address': email_, 'Address Line 1': address_1,
                'State Or County': address_2, 'Country': address_3 , 'Business Sector 1': 'Construction', 'Business Sector 2': 'Builders', 'email_grabber': 0}

            print(details)

      
            mycol.insert_one(details)

        except Exception as e:
            print(e)

        
        return
