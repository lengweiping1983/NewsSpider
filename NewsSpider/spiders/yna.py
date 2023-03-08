# -*- coding: utf-8 -*-
import scrapy
from NewsSpider.items import NewsItem
from NewsSpider.utils.date_utils import parse_str_get_date, date_to_str, timedelta_minutes
from NewsSpider.utils.str_utils import remove_blank, remove_blank_line, join_list
from NewsSpider.log import logger
from NewsSpider.spiders.base import BaseSpider


class YnaSpider(BaseSpider):
    name = "yna"
    allowed_domains = ["yna.co.kr"]
    start_urls = ["https://www.yna.co.kr"]

    def parse(self, response):
        logger.info('parse {}'.format(response.url))
        level1_menus = response.xpath('//*[@id="nav"]/ul/li')
        for level1 in level1_menus:
            main_category = level1.xpath('a/text()').extract_first()
            main_category = remove_blank(main_category)

            level2_menus = level1.xpath('div/dl/dd')
            for level2 in level2_menus:
                level2_category = level2.xpath('a/text()').extract_first()
                level2_category = remove_blank(level2_category)

                request_url = level2.xpath('a/@href').extract_first()
                request_url = response.urljoin(request_url)
                if request_url[-4:] != '/all':
                    category = main_category + "->" + level2_category
                    if self.check_url(request_url) and self.add_url(request_url):
                        if request_url.find('/nk/') > 0:
                            pass
                        else:
                            yield scrapy.Request(url=request_url, callback=self.parse_list,
                                                 meta={'main_category': main_category, 'category': category})

    def parse_list(self, response):
        logger.info('parse_list {}'.format(response.url))
        jump = True

        main_category = response.meta['main_category']
        category = response.meta['category']

        contents = response.xpath('//*[@id="container"]/div/div/div[1]')
        articles = contents.xpath('section/div[1]/ul/li')
        for article in articles:
            is_contains_content = article.xpath('div[contains(@class,"item-box01")]')
            if is_contains_content is None or len(is_contains_content) == 0:
                continue
            item = NewsItem()
            item['source'] = self.name
            item['is_video'] = 0

            title = article.xpath('div/div[2]/a/strong/text()').extract_first()
            date = article.xpath('div/div[1]/span[2]/text()').extract_first()

            img_url = article.xpath('div/figure/a/img/@src').extract_first()
            web_url = article.xpath('div/div[2]/a/@href').extract_first()

            if title and date and web_url:
                item['main_category'] = main_category
                item['category'] = category
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
                    jump = False
                    yield scrapy.Request(url=detail_page_url, callback=self.parse_detail, meta={'item_obj': item})

        if not jump:
            pagination = contents.xpath('section/div[contains(@class,"paging")]')
            if pagination and len(pagination) > 0:
                next_page_urls = pagination.xpath('a/@href').extract()
                for next_page_url in next_page_urls:
                    next_page_url = response.urljoin(next_page_url)
                    if self.check_url(next_page_url) and self.add_url(next_page_url):
                        yield scrapy.Request(url=next_page_url, callback=self.parse_list,
                                             meta={'main_category': main_category, 'category': category})

    def parse_detail(self, response):
        logger.info('parse_detail {}'.format(response.url))
        item_obj = response.meta['item_obj']
        content_list = []

        date = response.xpath('//*[@id="newsUpdateTime01"]').extract_first()
        if date is not None:
            publish_time = parse_str_get_date(date)
            item_obj['publish_time'] = date_to_str(publish_time)

        if len(content_list) == 0:
            body = response.xpath('//article[contains(@class,"story-news")]')
            if body is not None and len(body) > 0:
                content_list = response.xpath('//article[contains(@class,"story-news")]/text()|'
                                              '//article[contains(@class,"story-news")]/b/text()|'
                                              '//article[contains(@class,"story-news")]/p/text()|'
                                              '//article[contains(@class,"story-news")]/p/*/text()').extract()
                content_list = remove_blank_line(content_list)

        if content_list is not None and len(content_list) > 0:
            content = join_list(content_list)
            item_obj['content'] = content

        return item_obj
