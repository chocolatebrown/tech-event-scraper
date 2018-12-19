import scrapy
import re
from scrapy import signals
import json
from datetime import datetime
from dotenv import load_dotenv
import pyrebase
import os

load_dotenv()
event_data = {}
# set True to enable json file
json_enabled = True
config = {
            "apiKey": os.getenv('apiKey'),
            "authDomain": os.getenv('authDomain'),
            "databaseURL": os.getenv('databaseURL'),
            "storageBucket": os.getenv('storageBucket'),
            "serviceAccount": os.getenv('serviceAccount')
         }

firebase = pyrebase.initialize_app(config)
db = firebase.database()


class EventshighSpider(scrapy.Spider):
    name = "eventshigh_spider"
    start_urls = ['https://www.eventshigh.com/']
    event_data['Eventshigh Events'] = []

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(EventshighSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def parse(self, response):
        city_list = response.xpath("//div[@class='horizontal-container']//div[@class='f-s-16 p-t-16 cursor-pointer']//text()").extract()
        for city in city_list:
            tech_event_url = f"https://www.eventshigh.com/{city}/technology?src=cat-pill"
            yield scrapy.Request(tech_event_url, self.parse_event_data)

    def parse_event_data(self, response):
        for item in response.xpath("//div[@class='m-sm-lr-16 browse-events-wrp']//div[@class='d-inline-block event-card-wrp valign-top ga-card-track browse-card']"):
            event_title = item.xpath("a//div[@class='truncate f-s-16 f-s-sm-12 l-h-1p5 color-dark-grey']//text()").extract_first()
            date_string = item.xpath("a//div[@class='truncate f-s-16 f-s-sm-12 f-w-500 l-h-1p5 color-dark-grey']//text()").extract_first().strip()
            event_venue = item.xpath("a//div[@class='truncate f-s-16 f-s-sm-12 l-h-1p5 color-light-grey text-capitalize']//text()").extract_first()
            event_fee = item.xpath("a//div[@class='truncate f-s-16 f-s-sm-12 f-w-500 l-h-1p5 color-dark-grey'][2]/text()").extract_first()
            event_city = re.findall(".com/(.*)/technology", response.url)[0]
            event_keywords = ", ".join(item.xpath("div[@class='truncate']//a[@class='category-pill d-inline-block f-s-12 f-s-sm-8 f-w-sm-500 text-capitalize']//text()").extract())
            event_url = "https://www.eventshigh.com" + item.xpath("a/@href").extract_first()
            date_st = re.findall("[A-Z]{1}[a-z]{2}, ([0-9]{1,2} [A-Z]{1}[a-z]{2} [0-9]{0,4}) ?, ([0-9]{1,2}[:][0-9]{1,2}[A-Z]+)", date_string)
            try:
                event_date = datetime.strptime(date_st[0][0], "%d %b ").strftime(f"{datetime.now().year}-%m-%d")
            except ValueError:
                event_date = datetime.strptime(date_st[0][0], "%d %b %Y").strftime("%Y-%m-%d")
            except:
                event_date = date_string
            try:
                event_time = date_string[0][1]
            except IndexError:
                event_time = None
            except:
                event_time = None
            event_data['Eventshigh Events'].append({
                    'event_title': event_title,
                    'event_venue': event_venue,
                    'event_description': None,
                    'event_url': event_url,
                    'event_date': event_date,
                    'event_keywords': event_keywords,
                    'event_fee': event_fee,
                    'event_city': event_city,
                    'event_time': event_time,
                })
            db_data = {
                    'event_title': event_title,
                    'event_venue': event_venue,
                    'event_description': None,
                    'event_url': event_url,
                    'event_date': event_date,
                    'event_keywords': event_keywords,
                    'event_fee': event_fee,
                    'event_city': event_city,
                    'event_time': event_time,
                }
            db.child("tech-conferences").child("eventshigh").push(db_data)

    def spider_closed(self):
        if json_enabled:
            with open('../tech events/EventshighEvents.json', 'w', encoding='utf-8') as file:
                json.dump(event_data, file, ensure_ascii=False)


