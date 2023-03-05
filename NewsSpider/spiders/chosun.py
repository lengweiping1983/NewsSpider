# -*- coding: utf-8 -*-
import scrapy
import js2xml
import json
import datetime
from urllib.parse import parse_qs, urlencode, urlsplit, unquote
from NewsSpider.items import NewsItem
from NewsSpider.utils.date_utils import parse_str_get_date, date_to_str, timedelta_minutes
from NewsSpider.utils.str_utils import remove_blank, remove_blank_line, join_list
from NewsSpider.utils.url_utils import page_num_add_add, get_url_path
from NewsSpider.db.db_service import get_web_urls
from NewsSpider.log import logger
from NewsSpider.settings import INCREMENTAL_UPDATE


api_request_url_example = 'https://www.chosun.com/pf/api/v3/content/fetch/story-feed?query=%7B%22excludeContentTypes%22%3A%22gallery%2Cvideo%22%2C%22expandRelated%22%3Atrue%2C%22includeContentTypes%22%3A%22story%22%2C%22includeSections%22%3A%22%2Fsports%2Fbasketball%22%2C%22offset%22%3A20%2C%22size%22%3A20%7D&filter=%7Bcontent_elements%7B_id%2Ccanonical_url%2Ccredits%7Bby%7B_id%2Cadditional_properties%7Boriginal%7Baffiliations%2Cbyline%7D%7D%2Cname%2Corg%2Curl%7D%7D%2Cdescription%7Bbasic%7D%2Cdisplay_date%2Cheadlines%7Bbasic%2Cmobile%7D%2Clabel%7Bshoulder_title%7Btext%2Curl%7D%7D%2Clast_updated_date%2Cliveblogging_content%7Bbasic%7Bdate%2Cheadline%2Cid%2Curl%2Cwebsite%7D%7D%2Cpromo_items%7Bbasic%7B_id%2Cadditional_properties%7Bfocal_point%7Bmax%2Cmin%7D%7D%2Calt_text%2Ccaption%2Ccontent%2Ccontent_elements%7B_id%2Calignment%2Calt_text%2Ccaption%2Ccontent%2Ccredits%7Baffiliation%7Bname%7D%2Cby%7B_id%2Cbyline%2Cname%2Corg%7D%7D%2Cheight%2CresizedUrls%7B16x9_lg%2C16x9_md%2C16x9_sm%2C16x9_xs%2C16x9_xxl%2C4x3_lg%2C4x3_md%2C4x3_sm%2C4x3_xs%2C4x3_xxl%7D%2Csubtype%2Ctype%2Curl%2Cwidth%7D%2Ccredits%7Baffiliation%7Bbyline%2Cname%7D%2Cby%7Bbyline%2Cname%7D%7D%2Cdescription%7Bbasic%7D%2Cembed_html%2Cfocal_point%7Bx%2Cy%7D%2Cheadlines%7Bbasic%7D%2Cheight%2Cpromo_items%7Bbasic%7B_id%2Cheight%2CresizedUrls%7B16x9_lg%2C16x9_md%2C16x9_sm%2C16x9_xs%2C16x9_xxl%2C4x3_lg%2C4x3_md%2C4x3_sm%2C4x3_xs%2C4x3_xxl%7D%2Csubtype%2Ctype%2Curl%2Cwidth%7D%7D%2CresizedUrls%7B16x9_lg%2C16x9_md%2C16x9_sm%2C16x9_xs%2C16x9_xxl%2C4x3_lg%2C4x3_md%2C4x3_sm%2C4x3_xs%2C4x3_xxl%7D%2Cstreams%7Bheight%2Cwidth%7D%2Csubtype%2Ctype%2Curl%2Cwebsites%2Cwidth%7D%2Clead_art%7Bduration%2Ctype%7D%7D%2Crelated_content%7Bbasic%7B_id%2Cabsolute_canonical_url%2Cheadlines%7Bbasic%2Cmobile%7D%2Creferent%7Bid%2Ctype%7D%2Ctype%7D%7D%2Csubheadlines%7Bbasic%7D%2Csubtype%2Ctaxonomy%7Bprimary_section%7B_id%2Cname%7D%2Ctags%7Bslug%2Ctext%7D%7D%2Ctype%2Cwebsite_url%7D%2Ccount%2Cnext%7D&d=972&_website=chosun'


def get_value_by_key(obj, key):
    value = obj.get(key)
    if value is not None:
        return value
    for _, sub_obj in obj.items():
        if isinstance(sub_obj, dict):
            value = get_value_by_key(sub_obj, key)
            if value is not None:
                return value


def gen_api_request_url(section, page=1, size=20):
    offset = (page - 1) * size
    url = unquote(api_request_url_example)
    parsed = urlsplit(url)
    query_dict = parse_qs(parsed.query)
    query_str = '{"excludeContentTypes":"gallery,video","expandRelated":true,"includeContentTypes":"story","includeSections":"' + section + '","offset":' + str(
        offset) + ',"size":' + str(size) + '}'
    query_dict['query'][0] = query_str
    new_query = urlencode(query_dict, doseq=True)
    parsed = parsed._replace(query=new_query)
    api_request_url = parsed.geturl()
    return api_request_url


class ChosunSpider(scrapy.Spider):
    name = "chosun"
    allowed_domains = ["www.chosun.com"]
    start_urls = ["https://www.chosun.com"]

    max_pages = 30
    if INCREMENTAL_UPDATE:
        max_minutes = 60 * 24
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

    def parse(self, response):
        logger.info('parse {}'.format(response.url))
        level1_menus = response.xpath('//section[contains(@class,"sitemap-item")]')
        for level1 in level1_menus:
            main_category = level1.xpath('label/a/text()').extract_first()
            main_category = remove_blank(main_category)
            if main_category is None:
                continue
            level2_menus = level1.xpath('ul/li')
            for level2 in level2_menus:
                level2_category = level2.xpath('a/text()').extract_first()
                level2_category = remove_blank(level2_category)

                request_url = level2.xpath('a/@href').extract_first()
                request_url = response.urljoin(request_url)
                if request_url.find('/nsearch/') > 0:
                    continue
                category = main_category + "->" + level2_category
                # if self.check_url(request_url) and self.add_url(request_url):
                #     yield scrapy.Request(url=request_url, callback=self.parse_list,
                #                          meta={'main_category': main_category, 'category': category})
                query_page = 1
                query_section = get_url_path(request_url)
                api_request_url = gen_api_request_url(query_section, query_page)
                if self.check_url(api_request_url) and self.add_url(api_request_url):
                    yield scrapy.Request(url=api_request_url, callback=self.parse_api_list,
                                         meta={'main_category': main_category, 'category': category,
                                               'query_page': query_page, 'query_section': query_section})

    def parse_api_list(self, response):
        logger.info('parse_api_list {}'.format(response.url))
        jump = True

        main_category = response.meta['main_category']
        category = response.meta['category']
        query_page = response.meta['query_page']
        query_section = response.meta['query_section']
        try:
            contents = json.loads(response.text)
            contents = get_value_by_key(contents, "content_elements")
            for content in contents:
                item = NewsItem()
                item['source'] = self.name
                item['is_video'] = 0

                title = content.get("headlines").get("basic")
                date = content.get("display_date")
                img_urls = None
                if content.get("promo_items") is not None and content.get("promo_items").get("basic") is not None:
                    img_urls = content.get("promo_items").get("basic").get("resizedUrls")
                if img_urls is not None and len(img_urls) > 0:
                    img_url = img_urls.get("16x9_md")
                    if img_url is None:
                        img_url = list(img_urls.values())[0]
                web_url = content.get("canonical_url")

                if title and date and web_url:
                    item['main_category'] = main_category
                    item['category'] = category
                    item['title'] = remove_blank(title)

                    publish_time = parse_str_get_date(date) + datetime.timedelta(hours=9)
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
                query_page = query_page + 1 if query_page < self.max_pages else query_page
                api_request_url = gen_api_request_url(query_section, query_page)
                if self.check_url(api_request_url) and self.add_url(api_request_url):
                    yield scrapy.Request(url=api_request_url, callback=self.parse_api_list,
                                         meta={'main_category': main_category, 'category': category,
                                               'query_page': query_page, 'query_section': query_section})

        except Exception as e:
            logger.error('parse_api_list', str(e))

    def parse_list(self, response):
        logger.info('parse_list {}'.format(response.url))
        jump = True

        main_category = response.meta['main_category']
        category = response.meta['category']
        try:
            js = response.xpath('//script[contains(.,"Fusion.contentCache")]/text()').extract_first()
            xml = js2xml.parse(js)
            contents = xml.xpath('//assign[left//identifier[@name="contentCache"]]/right/*')
            contents = js2xml.make_dict(contents[0])

            contents = contents.get("story-feed")
            contents = get_value_by_key(contents, "content_elements")
            for content in contents:
                item = NewsItem()
                item['source'] = self.name
                item['is_video'] = 0

                title = content.get("headlines").get("basic")
                date = content.get("display_date")

                img_urls = None
                if content.get("promo_items") is not None and content.get("promo_items").get("basic") is not None:
                    img_urls = content.get("promo_items").get("basic").get("resizedUrls")
                if img_urls is not None and len(img_urls) > 0:
                    img_url = img_urls.get("16x9_md")
                    if img_url is None:
                        img_url = list(img_urls.values())[0]
                web_url = content.get("canonical_url")

                if title and date and web_url:
                    item['main_category'] = main_category
                    item['category'] = category
                    item['title'] = remove_blank(title)

                    publish_time = parse_str_get_date(date) + datetime.timedelta(hours=9)
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
                next_page_url = page_num_add_add(response.url, 'page', 2, self.max_pages)
                if self.check_url(next_page_url) and self.add_url(next_page_url):
                    yield scrapy.Request(url=next_page_url, callback=self.parse_list,
                                         meta={'main_category': main_category, 'category': category})

        except Exception as e:
            logger.error('parse_list', str(e))

    def parse_detail(self, response):
        logger.info('parse_detail {}'.format(response.url))
        item_obj = response.meta['item_obj']
        content_list = []

        try:
            js = response.xpath('//script[contains(.,"Fusion.globalContent")]/text()').extract_first()
            xml = js2xml.parse(js)
            contents = xml.xpath('//assign[left//identifier[@name="globalContent"]]/right/*')
            contents = js2xml.make_dict(contents[0])
            contents = get_value_by_key(contents, "content_elements")
            for content in contents:
                if content.get("type") == "text":
                    content_list.append(content.get("content"))
        except Exception as e:
            logger.error('parse_detail', str(e))

        if content_list is not None and len(content_list) > 0:
            content = join_list(content_list)
            item_obj['content'] = content

        return item_obj
