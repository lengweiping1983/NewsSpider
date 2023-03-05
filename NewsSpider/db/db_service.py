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
from NewsSpider.db.db_models import News, session, gen_web_url_md5
from NewsSpider.log import logging, logger


def add_news_to_db(item):
    try:
        instance = News(
            title=item.get("title"),
            content=item.get("content"),
            source_main_category=item.get("main_category"),
            source_category=item.get("category"),
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


def get_web_urls(source, last_update_time):
    web_urls = session.query(News.web_url).filter(
        and_(News.source == source, News.publish_time > last_update_time)).all()
    web_urls = [url for (url,) in web_urls]
    return web_urls


def test_db():
    # source = "demo.com"
    # last_update_time = timedelta_minutes(-2)
    # web_urls = get_web_urls(source, last_update_time)
    # print('web_urls', web_urls)
    pass


if __name__ == "__main__":
    test_db()
    pass
