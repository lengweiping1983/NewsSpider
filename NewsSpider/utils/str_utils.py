# -*- coding: utf-8 -*-
import re


def remove_blank(content, pattern='[\r|\n|\t]'):
    if content is None:
        return content
    return re.sub(pattern, '', content).strip()


def remove_blank_line(content_list):
    new_content_list = []
    for content in content_list:
        new_content = remove_blank(content)
        if len(new_content) > 0:
            new_content_list.append(new_content)
    return new_content_list


def join_list(content_list, pattern='\r\n'):
    return pattern.join(content_list)


def test():
    # content = ' \r\n\t\t\t\t\r\n\t\t\t'
    # print('content', content)
    # print('result', remove_blank(content))
    pass


if __name__ == '__main__':
    test()
