# -*- coding: utf-8 -*-
import hashlib


def get_md5(source):
    md5 = hashlib.md5()

    md5.update(source.encode('utf-8'))
    return md5.hexdigest()


def test_md5():
    source = "123456"
    print(get_md5(source))


if __name__ == "__main__":
    test_md5()
