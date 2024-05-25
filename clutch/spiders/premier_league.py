import scrapy
from scrapy import signals


import pymongo

myclient = pymongo.MongoClient(
    f"mongodb://localhost:27017"
)

mydb = myclient["premier_league"]

collection = mydb['players']

# collection.update_many({}, {"$set": {"player_image": 0}})


class QuotesSpider(scrapy.Spider):
    name = "epl"
    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(QuotesSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signals.spider_closed)
        return spider

    def spider_closed(self, spider):
        print("end")

    def start_requests(self):
        company_data = list(
            collection.find()
        )
        for player in company_data:
            yield scrapy.Request(
                url=player["player_image_url"],
                callback=self.parse_one,
            )

    def parse_one(self, response):

        print(response.url)

        player_image = response.css(
            "img.img::attr('data-player')"
        ).extract_first()

        player_image_url = f"https://resources.premierleague.com/premierleague/photos/players/250x250/{player_image}.png"

        id_ = int(response.url.split("/")[4])

        print(id_, player_image)

        collection.update_one({"player_id": id_}, { "$set": { 'player_image': player_image_url } })
