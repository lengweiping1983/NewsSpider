# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class NewsItem(scrapy.Item):
    # define the fields for your item here like:
    title = scrapy.Field()
    content = scrapy.Field()
    main_category = scrapy.Field()
    category = scrapy.Field()
    publish_time = scrapy.Field()
    img_url = scrapy.Field()
    web_url = scrapy.Field()
    is_video = scrapy.Field()
    source = scrapy.Field()

