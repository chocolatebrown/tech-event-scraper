import scrapy
import re
from scrapy import signals
import json

event_data = {}

class NasscomSpider(scrapy.Spider):
    name = "nasscom_spider"
    start_urls = ['https://www.nasscom.in/events']

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(NasscomSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def parse(self, response):
        event_data['Nasscom Events'] = []
        for item in response.xpath("//div[@class='view-content']//div[@class='item-list']//li"):
            event_title = item.xpath("div[@class='views-field views-field-title']//span//text()").extract_first().strip()
            event_url = 'https://www.nasscom.in' + item.xpath("div[@class='views-field views-field-title']//span//a/@href").extract_first()
            date_string = item.xpath("div[@class='views-field-field-event-time']//span//text()").extract_first()
            event_date = re.findall("(.*) \| (.*)",date_string)[0][0]
            event_time = re.findall("(.*) \| (.*)",date_string)[0][1]
            event_venue = item.xpath("div[@class='views-field-field-description-security']//div//text()").extract_first().strip()
            event_data['Events'].append(
                        {
                            'event_title': event_title,
                            'event_date': event_date,
                            'event_time': event_time,
                            'event_venue': event_venue,
                            'event_url': event_url
                        })

    def spider_closed(self):
        with open('tech events/NasscomEvent.json', 'w') as file:
            json.dump(event_data, file)






