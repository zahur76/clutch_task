from dataclasses import replace
from time import time

import scrapy


start_url = {'url': 'https://clutch.co/agencies/event', 'category': False, 'subcategory': False, 'details': False}

# max_query = 2
# query_list = []

# property_list = []

# links_required = []
# count = []

page_links = []

page = []

# limit pages crawled can be changed
page_crawled = 1

company_dict = []

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

        """
            Extract all company links on all pages 50 * 80
        """

        # limit pages crawled
        page.append(1)

        if  len(page) <= page_crawled:
            try:
                next = response.css("li.page-item.next").get()
            except:
                next = None
            
            if next:
                links = response.css("a.company_logotype::attr('href')").extract()
                for link in links:
                    page_links.append(link)
                next_page = response.css("li.page-item.next a.page-link::attr('href')").extract()[0]
                new_link = response.urljoin(next_page)
                yield scrapy.Request(url=new_link, callback=self.parse_one, dont_filter=True)
            else:
                links = response.css("a.company_logotype::attr('href')").extract()
                for link in links:
                    page_links.append(link)
        else:
            for link in page_links:
                send_link = response.urljoin(link)
                yield scrapy.Request(url=send_link, callback=self.parse_two, dont_filter=True)

        
    def parse_two(self, response):

        """ 
            Extract company information from details page
        """

        #company name
        company_name = response.css('h1.header-company--title a::text').get().replace("\n","").strip()

        # company image
        company_image = response.css('img.header-company--logotype::attr(src)').get()

        # company url
        company_url = response.css("h1.header-company--title a::attr('href')").get()

        # company verification status
        try:
            verification_status = response.css('div.verification-status-wrapper::text').extract()[1].replace("\n","").strip()
        except:
            verification_status = None

        # company rating
        rating = response.css('span.rating::text').get().strip()

        # company review count
        review_count = response.css('a.reviews-link span::text').get().strip()

        # company decsription
        descriptions = response.css('div.field-name-profile-summary p::text').extract()

        combined_desciption = ""
        for description in descriptions:
            combined_desciption += description        
        
        combined_desciption.strip()

        # company general info (Project size, Hourly rate, employees, founded, languages, timezone)
        company_info = response.css('div.module-list div.list-item span::text').extract()

        try:
            languages = company_info[4].strip()
        except:
            languages = None

        try:
            timezone = company_info[5].strip()
        except:
            timezone =  None

        # address

        street_address = response.css('div.street-address::text').get()       

        locality = response.css('span.locality::text').get()

        region = response.css('span.region::text').get()

        postal_code = response.css('span.postal-code::text').get()

        country = response.css('div.country-name::text').get()


        combined_address = [street_address, locality, region, postal_code, country]

        corrected_address = ""

        for address in combined_address:
            if address:
                corrected_address += f'{address}, '

        # Phone Number
        try:
            phone_number = response.css('li.quick-menu-details a::text').get().replace(".", "").strip()
        except:
            phone_number = response.css('li.quick-menu-details a::text').get()

        # focus section

        focust_list = response.css('div.graph-title::text').extract()
        focus_dict = {company_name: []}

        for item in focust_list:
            data_ = ''
            try: 
                data_one = response.xpath(f"//*[contains(text(), '{item}')]/../div[2]/div/div/@data-content").extract()
                percentage_list = []
                item_list = []
                for item__ in data_one:
                    if '<i>' not in item__:
                        item_ = item__.replace('<b>', '').replace('</b>', '')
                        item_list.append(item_)
                        percent_ = response.css(f"div[data-content='{item__}']::text").extract_first()
                        if percent_:
                            percentage_list.append(percent_)
                        else:
                            percentage_list.append(response.css(f"div[data-content='{item__}'] > span::text").extract_first())
                    else:
                        item_ = item__.split('</i>')
                        item_list.append(item_[1].replace('<b>', '').replace('</b>', ''))
                        percent_value = item_[0].replace('<i>', '')                        
                        percentage_list.append(percent_value)
                        

                for j in range(len(data_one)):
                    data_ += f'{item_list[j]}: {percentage_list[j]}, '
                data_ = data_[:-2]
                focus_dict[company_name].append({item: data_})
            except Exception as e:
                data_ = None
        

        # Portfolio section
    
        key_clients = response.css('div.field-name-clients div p::text').extract()

        if not key_clients:
            key_clients = None
        else:
            key_clients = key_clients[0].replace("\x80\x99s", "").replace("â\x80\x9c", "").replace(".â\x80\x9d", "").replace("\xa0", "")


        company_dict.append({"Company": company_name,
                                "Company_Url": company_url,
                                "Company_image": company_image,
                                "Address":corrected_address[:-2],
                                "Phone_number": phone_number,
                                "Description": combined_desciption,
                                "Verification Status": verification_status, 
                                "rating": rating, 
                                "review_count": review_count,
                                "Min_Project_Size": company_info[0], 
                                "Avg_hour_rate": company_info[1].strip(), 
                                "Employees": company_info[2].strip(), 
                                "Founded": company_info[3].strip(), 
                                "Languages": languages,
                                "Timezone": timezone,
                                "Focus": focus_dict[company_name],
                                "Portfolio": key_clients                                                    
                                })
      

        if len(company_dict) == 50:
            print(company_dict[0])