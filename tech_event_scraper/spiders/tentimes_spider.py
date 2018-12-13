import scrapy
import requests
import re
from scrapy import signals
import json

event_data = {}
cookies = {"linkedin_oauth_ro57ogahnixy": "null", "linkedin_oauth_ro57ogahnixy_crc": "null", "10T_ping": "0#$No#$No", "10T_ntfs": "1-t"}
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.80 Safari/537.36',
           'x-requested-with': 'XMLHttpRequest',
           'referer': 'https://10times.com/technology'}
class TentimesSpider(scrapy.Spider):
    name = "tentimes_spider"
    start_urls = ['https://10times.com/technology']
    event_data['10times Events'] = []

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(TentimesSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def parse(self, response):
        page_num = 1
        while True:
            r = requests.get(f'https://10times.com/ajax?for=scroll&path=/technology&ajax=1&page={page_num}&popular=1',
                         headers=headers, params=cookies)
            page_num += 1
            if r.status_code == 200:
                res = scrapy.Selector(text=r.content.decode('utf-8'), type='html')
                for j, row in enumerate(res.xpath("//tr[@class='box']")):
                    if not row.xpath("td[@colspan='6' and @class='tb-foot']"):
                        date_string = row.xpath("td[1]//text()").extract()
                        try:
                            event_date = date_string[0]
                            event_status = date_string[1]
                        except IndexError:
                            event_date = date_string[0]
                            event_status = ''
                        event_url = row.xpath("td[2]//a/@href").extract_first()
                        event_title = row.xpath("td[2]//text()").extract_first()
                        event_venue = ",".join(row.xpath("td[3]//a//text()").extract())
                        event_description = row.xpath("td[4]//text()").extract_first()
                        event_data['10times Events'].append(
                            {
                                'event_title': event_title,
                                'event_date': event_date,
                                'event_status': event_status,
                                'event_venue': event_venue,
                                'event_description': event_description,
                                'event_url': event_url
                            })
            elif r.status_code == 403:
                break

    def spider_closed(self):
        with open('10times.json', 'w') as file:
            json.dump(event_data, file)

