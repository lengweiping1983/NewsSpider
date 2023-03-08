import os
import sys
import datetime
import traceback

from sqlalchemy import (
    and_,
    or_,
)

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from NewsSpider.utils.date_utils import timedelta_minutes
from NewsSpider.db.db_models import session
from NewsSpider.db.db_models import News, Category, CategoryMapping, OnlineStatus
from NewsSpider.db.db_models import gen_web_url_md5
from NewsSpider.log import logging, logger


def get_web_urls(source, last_update_time):
    web_urls = session.query(News.web_url).filter(
        and_(News.source == source, News.publish_time > last_update_time)).all()
    web_urls = [url for (url,) in web_urls]
    return web_urls


def get_all_categorys():
    categorys = session.query(Category).all()
    return categorys


def get_all_category_mappings():
    category_mappings = session.query(CategoryMapping).all()
    return category_mappings


category_name_to_code_dict = dict()
category_mapping_dict = dict()


def init_data():
    categorys = get_all_categorys()
    category_mappings = get_all_category_mappings()

    for category in categorys:
        category_name_to_code_dict[category.name] = category.code

    for category_mapping in category_mappings:
        if category_mapping.source is not None:
            category_mapping_dict[category_mapping.source + "---" + category_mapping.source_main_category] = \
                category_mapping.category
        else:
            category_mapping_dict[category_mapping.source_main_category] = category_mapping.category


init_data()


def add_news_to_db(item):
    try:
        category = None
        category_code = None
        status = OnlineStatus.WAITING.value
        if item['main_category'] is not None:
            category = category_mapping_dict.get(item['source'] + "---" + item['main_category'])
            if category is None:
                category = category_mapping_dict.get(item['main_category'])
            if category is not None:
                category_code = category_name_to_code_dict[category]
                status = OnlineStatus.ONLINE.value

        instance = News(
            title=item.get("title"),
            content=item.get("content"),
            source_main_category=item.get("main_category"),
            source_category=item.get("category"),
            category=category,
            category_code=category_code,
            status=status,
            publish_time=item.get("publish_time"),
            img_url=item.get("img_url"),
            web_url=item.get("web_url"),
            is_video=item.get("is_video"),
            source=item.get("source"),
        )
        gen_web_url_md5(instance)
        session.add(instance)
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error('add_news_to_db', str(e))
        # traceback.print_exc()
    finally:
        session.close()


def test_db():
    # source = "demo.com"
    # last_update_time = timedelta_minutes(-2)
    # web_urls = get_web_urls(source, last_update_time)
    # print('web_urls', web_urls)
    pass


if __name__ == "__main__":
    test_db()
    pass
