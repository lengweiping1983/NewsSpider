# -*- coding: utf-8 -*-
import scrapy
from NewsSpider.items import NewsItem
from NewsSpider.utils.date_utils import parse_str_get_date, date_to_str, timedelta_hours
from NewsSpider.utils.url_utils import page_num_add_add
from NewsSpider.utils.str_utils import remove_blank, remove_blank_line, join_list
from NewsSpider.db.db_service import get_web_urls
from NewsSpider.log import logger


class KbsSpider(scrapy.Spider):
    name = "kbs"
    allowed_domains = ["world.kbs.co.kr", "news.kbs.co.kr"]
    lang_url = "lang=k"
    start_urls = ["http://world.kbs.co.kr/service/index.htm?" + lang_url]

    max_pages = 20
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
        if request_url.find(self.allowed_domains[0]) > 0 and \
                request_url.find(self.lang_url) > 0 \
                and request_url.find("_list.htm") > 0:
            return True
        return False

    def add_url(self, request_url):
        if request_url not in self.all_request_urls:
            self.all_request_urls.add(request_url)
            return True
        return False

    def parse(self, response):
        logger.info('parse {}'.format(response.url))
        menus = response.xpath('//div[@class="menu_2depth"]')
        request_urls = menus[:3].xpath('*//a/@href').extract()
        for request_url in request_urls:
            request_url = response.urljoin(request_url)
            if self.check_url(request_url) and self.add_url(request_url):
                yield scrapy.Request(url=request_url, callback=self.parse_list)

    def parse_list(self, response):
        logger.info('parse_list {}'.format(response.url))
        jump = False

        contents = response.xpath('//*[@id="container"]/div')
        main_category = contents.xpath('h1/text()').extract_first()
        if main_category is None:
            main_category = contents.xpath('section/h1/text()').extract_first()
        main_category = remove_blank(main_category)

        articles = contents.xpath('section/article')
        for article in articles:
            item = NewsItem()
            item['source'] = self.name
            item['is_video'] = 0

            category = article.xpath('p[1]/a/text()').extract_first()
            title = article.xpath('h2[1]/a/text()').extract_first()
            date = article.xpath('p[2]/text()').extract_first()
            if title is None or date is None:
                title = article.xpath('div[2]/a/h2[1]/text()').extract_first()
                date = article.xpath('div[2]/a/p[1]/text()').extract_first()

            img_url = article.xpath('div[1]/a/img/@src').extract_first()
            web_url = article.xpath('div[1]/a/@href').extract_first()

            is_video = article.xpath('div[1]/a/i[@class="vod"]').extract_first()
            if is_video is not None:
                item['is_video'] = 1

            if title and date and web_url:
                if category is None or '#' in category:
                    item['category'] = main_category
                else:
                    item['category'] = remove_blank(category)
                item['main_category'] = item['category']
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
            pagination = contents.xpath('section/article/div[contains(@class,"pagination")]')
            if pagination and len(pagination) > 0:
                next_page_url = page_num_add_add(response.url, 'page', 2, self.max_pages)
                if self.check_url(next_page_url) and self.add_url(next_page_url):
                    yield scrapy.Request(url=next_page_url, callback=self.parse_list)

    def parse_detail(self, response):
        logger.info('parse_detail {}'.format(response.url))
        item_obj = response.meta['item_obj']
        content_list = []

        if len(content_list) == 0:
            body = response.xpath('//div[contains(@class,"body_txt")]')
            if body is not None and len(body) > 0:
                content_list = response.xpath('//div[contains(@class,"body_txt")]/text()|'
                                              '//div[contains(@class,"body_txt")]/b/text()|'
                                              '//div[contains(@class,"body_txt")]/p/text()|'
                                              '//div[contains(@class,"body_txt")]/p/*/text()').extract()
                content_list = remove_blank_line(content_list)

            if len(content_list) == 0:
                body = response.xpath('//div[contains(@class,"body_txt")]/div[2]')
                if body is not None and len(body) > 0:
                    content_list = response.xpath('//div[contains(@class,"body_txt")]/div[2]/text()|'
                                                  '//div[contains(@class,"body_txt")]/div[2]/b/text()|'
                                                  '//div[contains(@class,"body_txt")]/div[2]/p/text()|'
                                                  '//div[contains(@class,"body_txt")]/div[2]/p/*/text()').extract()
                    content_list = remove_blank_line(content_list)

        if len(content_list) == 0:
            body = response.xpath('//div[contains(@class,"detail-body")]')
            if body is not None and len(body) > 0:
                content_list = response.xpath('//div[contains(@class,"detail-body")]/text()|'
                                              '//div[contains(@class,"detail-body")]/b/text()|'
                                              '//div[contains(@class,"detail-body")]/p/text()|'
                                              '//div[contains(@class,"detail-body")]/p/*/text()').extract()
                content_list = remove_blank_line(content_list)

        if content_list is not None and len(content_list) > 0:
            content = join_list(content_list)
            item_obj['content'] = content

        return item_obj
