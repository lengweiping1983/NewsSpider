# -*- coding: utf-8 -*-
from urllib.parse import parse_qs, urlencode, urlsplit


def page_num_add_add(url, param, init_value=1, max_value=-1):
    if url is None:
        return url
    parsed = urlsplit(url)
    query_dict = parse_qs(parsed.query)
    if query_dict.get(param) is not None:
        query_dict[param][0] = int(query_dict[param][0]) + 1
    else:
        query_dict[param] = [init_value]
    new_query = urlencode(query_dict, doseq=True)
    parsed = parsed._replace(query=new_query)
    if query_dict[param][0] > max_value > 0:
        return url
    return parsed.geturl()


def get_url_path(url):
    if url is None:
        return url
    parsed = urlsplit(url)
    return parsed.path


def get_url_query_dict(url):
    if url is None:
        return url
    parsed = urlsplit(url)
    query_dict = parse_qs(parsed.query)
    return query_dict


def test():
    # url = 'http://world.kbs.co.kr/service/news_list.htm?lang=c'
    # url = 'http://world.kbs.co.kr/service/news_list.htm?page=2&lang=c'
    # print(page_num_add_add(url, 'page', 2))

    url = 'https://www.yna.co.kr/view/AKR20230220064900056?section=lifestyle/travel-festival'
    url_path = get_url_path(url)
    query_dict = get_url_query_dict(url)
    print(url_path)
    print(query_dict)


if __name__ == '__main__':
    test()
