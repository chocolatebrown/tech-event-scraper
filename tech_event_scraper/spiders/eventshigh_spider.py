import scrapy
import re
from scrapy import signals
import json

event_data = {}

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
            event_date = item.xpath("a//div[@class='truncate f-s-16 f-s-sm-12 f-w-500 l-h-1p5 color-dark-grey']//text()").extract_first().strip()
            event_venue = item.xpath("a//div[@class='truncate f-s-16 f-s-sm-12 l-h-1p5 color-light-grey text-capitalize']//text()").extract_first()
            event_description = item.xpath("a//div[@class='truncate f-s-16 f-s-sm-12 f-w-500 l-h-1p5 color-dark-grey'][2]/text()").extract_first()
            event_city = re.findall(".com/(.*)/technology", response.url)[0]
            event_url = "https://www.eventshigh.com" + item.xpath("a/@href").extract_first()
            event_data['Eventshigh Events'].append(
                {
                    'event_title': event_title,
                    'event_date': event_date,
                    'event_venue': event_venue,
                    'event_city': event_city,
                    'event_description': event_description,
                    'event_url': event_url
                })
            print(event_data)

    def spider_closed(self):
        with open('EventshighEvents.json', 'w', encoding='utf-8') as file:
            json.dump(event_data, file, ensure_ascii=False)




