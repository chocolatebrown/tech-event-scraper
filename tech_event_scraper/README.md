# Tech Event Scraper

Python crawler to fetch technology events & conferences from various websites and platform.


# Requirements

    pip install scrapy
 
# To Run the Script

create a spider_execution.py file and change the spider name in the argument to run the specified spider.
spider name can be found under spiders directory.
 

    import scrapy
    from scrapy.cmdline import execute
    
    execute(['scrapy', 'crawl', 'nasscom_spider'])

Execute the spider_execution file which will run the appropriate site crawler.

# Output

Currently the Spider will only produce json.

