import scrapy
import json
import os
import requests

start_url = {'url': 'https://clutch.co/agencies/event', 'category': False, 'subcategory': False, 'details': False}

# max_query = 2
# query_list = []

# property_list = []

# links_required = []
# count = []

page_links = []

class QuotesSpider(scrapy.Spider):
    name = "clutch"

    def start_requests(self):
        url = start_url
        if not url['category'] and not url['subcategory'] and not url['details']:
            yield scrapy.Request(url=url['url'], callback=self.parse_one)
        if url['category'] and not url['subcategory'] and not url['details']:
            yield scrapy.Request(url=url['url'], callback=self.parse_two)
        if url['category'] and url['subcategory'] and not url['details']:
            yield scrapy.Request(url=url['url'], callback=self.parse_three)

    def parse_one(self, response):
        
        try:
            next = response.css("li.page-item.next").get()
        except:
            next = None

        if next:
            links = response.css("a.company_logotype::attr('href')").extract()
            for link in links:
                page_links.append(link)
            # print(page_links)
            next_page = response.css("li.page-item.next a.page-link::attr('href')").extract()[0]
            new_link = response.urljoin(next_page)
            print(new_link)
            yield scrapy.Request(url=new_link, callback=self.parse_one, dont_filter=True)
        else:
            links = response.css("a.company_logotype::attr('href')").extract()
            for link in links:
                page_links.append(link)
            # print(page_links)
            print(len(page_links))


    