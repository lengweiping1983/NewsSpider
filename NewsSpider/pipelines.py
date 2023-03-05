# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from NewsSpider.db.db_service import add_news_to_db


class NewsspiderPipeline:
    def process_item(self, item, spider):
        add_news_to_db(item)
        return item
