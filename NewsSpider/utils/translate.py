import os
import time
from nlpcda import baidu_translate

baidu_appId = '20220722001280061'
baidu_secretKey = '637yfqZBQCVV1MatQywv'


def translate(text, t_from='kor', t_to='en'):
    if text:
        return baidu_translate(content=text, appid=baidu_appId, secretKey=baidu_secretKey, t_from=t_from, t_to=t_to)
    return text


def test():
    text = '문화'
    # print(translate(text, t_to='en'))
    time.sleep(1.5)
    # print(translate(text, t_to='zh'))
    pass


if __name__ == '__main__':
    test()
