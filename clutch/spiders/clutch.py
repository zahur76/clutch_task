import scrapy
import json
import os
import requests

start_url = {'url': 'https://nigeriapropertycentre.com/', 'category': False, 'subcategory': False, 'details': False}

max_query = 2
query_list = []

property_list = []

links_required = []
count = []

class QuotesSpider(scrapy.Spider):
    name = "property"

    def start_requests(self):
        url = start_url
        if not url['category'] and not url['subcategory'] and not url['details']:
            yield scrapy.Request(url=url['url'], callback=self.parse_one)
        if url['category'] and not url['subcategory'] and not url['details']:
            yield scrapy.Request(url=url['url'], callback=self.parse_two)
        if url['category'] and url['subcategory'] and not url['details']:
            yield scrapy.Request(url=url['url'], callback=self.parse_three)

    def parse_one(self, response):
        link = response.css('li a[href="/for-sale"]::attr("href")').get()
        new_link = response.urljoin(link)
        yield scrapy.Request(url=new_link, callback=self.parse_two)  

    