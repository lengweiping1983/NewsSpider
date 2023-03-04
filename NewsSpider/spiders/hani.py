# -*- coding: utf-8 -*-
import scrapy
from NewsSpider.items import NewsItem
from NewsSpider.utils.date_utils import parse_str_get_date, date_to_str, timedelta_hours
from NewsSpider.utils.str_utils import remove_blank, remove_blank_line, join_list
from NewsSpider.db.db_service import get_web_urls
from NewsSpider.log import logger


class HaniSpider(scrapy.Spider):
    name = "hani"
    allowed_domains = ["hani.co.kr"]
    start_urls = ["https://www.hani.co.kr/arti"]

    max_hours = 10 * 24
    last_update_time = timedelta_hours(hours=-max_hours)

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

    def parse(self, response):
        logger.info('parse {}'.format(response.url))
        return self.parse_list(response)

    def parse_list(self, response):
        logger.info('parse_list {}'.format(response.url))
        jump = False

        contents = response.xpath('//*[@id="section-left-scroll-in"]')
        articles = contents.xpath('div/div/div[contains(@class,"article-area")]')
        for article in articles:
            item = NewsItem()
            item['source'] = self.name
            item['is_video'] = 0

            category = article.xpath('strong/a/text()').extract_first()
            title = article.xpath('h4/a/text()').extract_first()
            date = article.xpath('p/span/text()').extract_first()

            img_url = article.xpath('span/a/img/@src').extract_first()
            web_url = article.xpath('h4/a/@href').extract_first()

            if title and date and web_url:
                item['category'] = remove_blank(category)
                item['main_category'] = item['category']
                if item['category'] in ['English Edition']:
                    continue
                item['title'] = remove_blank(title)

                publish_time = parse_str_get_date(date)
                if publish_time is None or self.last_update_time > publish_time:
                    jump = True
                    break
                item['publish_time'] = date_to_str(publish_time)

                if img_url:
                    item['img_url'] = response.urljoin(remove_blank(img_url))
                item['web_url'] = response.urljoin(remove_blank(web_url))

                detail_page_url = item['web_url']
                if self.add_url(detail_page_url):
                    yield scrapy.Request(url=detail_page_url, callback=self.parse_detail, meta={'item_obj': item})

        if not jump:
            pagination = contents.xpath('div[contains(@class,"paginate")]')
            if pagination and len(pagination) > 0:
                next_page_urls = pagination.xpath('a/@href').extract()
                for next_page_url in next_page_urls:
                    next_page_url = response.urljoin(next_page_url)
                    if self.check_url(next_page_url) and self.add_url(next_page_url):
                        yield scrapy.Request(url=next_page_url, callback=self.parse_list)

    def parse_detail(self, response):
        logger.info('parse_detail {}'.format(response.url))
        item_obj = response.meta['item_obj']
        content_list = []

        if len(content_list) == 0:
            body = response.xpath('//div[contains(@class,"article-text")]/div/div')
            if body is not None and len(body) > 0:
                content_list = response.xpath('//div[contains(@class,"article-text")]/div/div/text()|'
                                              '//div[contains(@class,"article-text")]/div/div/b/text()|'
                                              '//div[contains(@class,"article-text")]/div/div/p/text()').extract()
                content_list = remove_blank_line(content_list)

        if content_list is not None and len(content_list) > 0:
            content = join_list(content_list)
            item_obj['content'] = content

        return item_obj
