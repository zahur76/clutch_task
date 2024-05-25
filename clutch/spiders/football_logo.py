import scrapy
import json
import os

max_query = 10000

image_dictionary = {}

f = open('./data/team_names.json')
data = json.load(f)


import pymongo

myclient = pymongo.MongoClient(
    f"mongodb://localhost:27017"
)

mydb = myclient["football"]


class QuotesSpider(scrapy.Spider):
    name = "team-logos"

    def start_requests(self):
        
            
        url = f'https://www.glassdoor.com/Explore/browse-companies.htm?overall_rating_low=3.5&page=999&sector=10010&filterType=RATING_OVERALL'
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        print(response.url)
   
        # image_url = response.css(".iusc::attr('href')").get()

        # new_link = response.urljoin(image_url)

        # yield scrapy.Request(url=new_link, callback=self.parse_two, meta={'company': company})

    def parse_two(self, response):
        # bing and clearbit logo image scrapping
        bing_image_url = response.css('img::attr("src")').extract_first()
        print(bing_image_url, response.meta['company'])
        
        mydb["football_logos"].insert_one({"url": bing_image_url, "name": response.meta['company']})

        # if bing_image_url == '/sa/simg/Flag_Feedback.png':
        #     url = f'https://www.bing.com/images/search?q={response.meta["company"]}'
        #     yield scrapy.Request(url=url, callback=self.parse_four, meta={'company': response.meta['company']})
        
        # else:            
        #     company_url = data[0][response.meta['company']
        #                         ]['company_url'].split('//')[1]

        #     image_dictionary[f'{response.meta["company"]}'] = [
        #         {'bing_image': bing_image_url}, {'clearbit_image': f'https://logo.clearbit.com/{company_url}'}]
            
        #     try:
        #         wikipedia_url = data[0][response.meta['company']]['wikipedia_url']
        #     except:
        #         wikipedia_url = None
            
            
        #     if not wikipedia_url:
        #         wikipedia_url = 'https://www.google.com'
            
        #     yield scrapy.Request(url=wikipedia_url, callback=self.parse_three, meta={'company': response.meta['company']}, dont_filter=True)

    def parse_three(self, response):
        # wikipedia image

        if response.url == 'https://www.google.com':
            wikipedia_image = None

            image_dictionary[f'{response.meta["company"]}'].append(
            {'wikipedia_image': None})
        else:
            try:
                wikipedia_image = response.css(
                    '.infobox-image a img::attr("src")').get()
            except:
                wikipedia_image = None

            image_dictionary[f'{response.meta["company"]}'].append(
                {'wikipedia_image': response.urljoin(wikipedia_image)})

        try:
            json_data = json.dumps(image_dictionary, ensure_ascii=False)
            json_data = json_data.replace('\\"', '')
            filename = 'company_images'
            if not os.path.exists('data'):
                os.makedirs('data')

            with open(f'./data/{filename}.json', 'w', encoding='utf-8') as out:
                out.write(json_data)
        except Exception as e:
            print(e)


    def parse_four(self, response):
        print('======================')
        print(response.url)
        # bing and clearbit logo image scrapping
        bing_image_url = response.css('.iusc img::attr("src")').extract_first()
                  
        company_url = data[0][response.meta['company']
                            ]['company_url'].split('//')[1]

        image_dictionary[f'{response.meta["company"]}'] = [
            {'bing_image': bing_image_url}, {'clearbit_image': f'https://logo.clearbit.com/{company_url}'}]
        
        try:
            wikipedia_url = data[0][response.meta['company']]['wikipedia_url']
        except:
            wikipedia_url = None
        
        
        if not wikipedia_url:
            wikipedia_url = 'https://www.google.com'
        
        yield scrapy.Request(url=wikipedia_url, callback=self.parse_three, meta={'company': response.meta['company']}, dont_filter=True)
