# -*- coding: utf-8 -*-
from abc import ABC

import scrapy
from NewsSpider.utils.date_utils import parse_str_get_date, date_to_str, timedelta_minutes
from NewsSpider.db.db_service import get_web_urls
from NewsSpider.settings import INCREMENTAL_UPDATE


class BaseSpider(scrapy.Spider, ABC):
    name = ""
    allowed_domains = [""]

    max_pages = 100
    if INCREMENTAL_UPDATE:
        max_minutes = 60 * 24 * 2
    else:
        max_minutes = 60 * 24 * 30 * 6
    last_update_time = timedelta_minutes(minutes=-max_minutes)

    all_request_urls = set()

    def __init__(self):
        for url in self.start_urls:
            self.all_request_urls.add(url)
        web_urls = get_web_urls(self.name, self.last_update_time)
        for url in web_urls:
            self.all_request_urls.add(url)

    def check_url(self, request_url):
        if request_url.find(self.allowed_domains[0]) > 0:
            return True
        return False

    def add_url(self, request_url):
        if request_url not in self.all_request_urls:
            self.all_request_urls.add(request_url)
            return True
        return False
