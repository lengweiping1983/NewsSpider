# -*- coding: utf-8 -*-
import os
import sys
import datetime
import traceback
from enum import Enum
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    UniqueConstraint,
    Index,
    exists,
    and_,
    or_,
)
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.ext.declarative import declarative_base

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from NewsSpider.utils.md5 import get_md5
from NewsSpider.log import logger, logging


# 基础类
Base = declarative_base()

# 创建引擎
engine = create_engine(
    "mysql+pymysql://root:123456@127.0.0.1:3306/news?charset=utf8",
    # 超过链接池大小外最多创建的链接
    max_overflow=0,
    # 链接池大小
    pool_size=5,
    # 链接池中没有可用链接则最多等待的秒数，超过该秒数后报错
    pool_timeout=10,
    # 多久之后对链接池中的链接进行一次回收
    pool_recycle=1,
    # 查看原生语句（未格式化）
    echo=True
)


# 绑定引擎
Session = sessionmaker(bind=engine)
# 创建数据库链接池，直接使用session即可为当前线程拿出一个链接对象conn
# 内部会采用threading.local进行隔离
session = scoped_session(Session)


class HandleStatus(Enum):
    WAITING = 0
    RUNNING = 1
    SUCCEEDED = 2
    FAILED = 3


class OnlineStatus(Enum):
    WAITING = 0
    ONLINE = 1
    OFFLINE = 2


class News(Base):
    # 数据库中存储的表名
    __tablename__ = "n_news"
    # 对于必须插入的字段，采用nullable=False进行约束，它相当于NOT NULL
    id = Column(Integer, primary_key=True, autoincrement=True, comment="id")
    title = Column(String(255), nullable=False, index=True, comment="title")

    content = Column(LONGTEXT, comment="content")
    img_url = Column(String(255), comment="img_url")
    web_url = Column(String(1024), nullable=False, comment="web_url")
    web_url_md5 = Column(String(255), nullable=False, unique=True, comment="web_url_md5")
    is_video = Column(Boolean(), default=False, comment="is_video")
    publish_time = Column(DateTime, index=True, default=datetime.datetime.now, comment="publish_time")

    source = Column(String(32), comment="source")
    source_main_category = Column(String(64), comment="source_main_category")
    source_category = Column(String(255), comment="source_category")
    category = Column(String(255), index=True, comment="category")
    category_code = Column(String(255), index=True, comment="category_code")

    status = Column(Integer, default=0, comment="status")
    delete_status = Column(Boolean(), default=False, comment="delete_status")

    reason = Column(String(1024), comment="reason")
    category_en = Column(String(255), comment="category_en")
    content_en = Column(LONGTEXT, comment="content_en")

    create_time = Column(DateTime, default=datetime.datetime.now, comment="create_time")
    last_update_time = Column(DateTime, onupdate=datetime.datetime.now, comment="last_update_time")

    __table__args__ = (
        UniqueConstraint("title", "source"),            # 联合唯一约束
        UniqueConstraint("title", "delete_status"),     # 联合唯一约束
        Index("title", "source", unique=True),          # 联合唯一索引
        Index("category_code", "publish_time"),         # 联合索引
        Index("category", "publish_time"),              # 联合索引
    )

    def __str__(self):
        return f"object : <id:{self.id} title:{self.title}>"


def gen_web_url_md5(obj):
    obj.web_url_md5 = get_md5(obj.web_url)


def add():
    try:
        instance = News(
            title="title1",
            content="content1",
            web_url="www.demo.com/1",
            source="demo.com",
        )
        gen_web_url_md5(instance)
        session.add(instance)

        instance = News(
            title="title2",
            content="content2",
            web_url="www.demo.com/2",
            source="demo.com",
        )
        gen_web_url_md5(instance)
        session.add(instance)

        instance = News(
            title="title3",
            content="content3",
            web_url="www.demo.com/3",
            source="demo.com",
        )
        gen_web_url_md5(instance)
        session.add(instance)
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error('add error', str(e))
        traceback.print_exc()
    finally:
        session.close()


def update():
    try:
        session.query(News).filter_by(title="title2").update(
            {
                "title": News.title + " update"
            },
            synchronize_session=False
        )
        # 本次修改具有字符串字段在原值基础上做更改的操作，所以必须添加
        # synchronize_session=False
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error('update error', str(e))
        traceback.print_exc()
    finally:
        session.close()


def delete():
    try:
        session.query(News).filter_by(title="title3").delete()
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error('delete error', str(e))
        traceback.print_exc()
    finally:
        session.close()


def test_db():
    add()
    update()
    delete()


if __name__ == "__main__":
    # 删除表
    Base.metadata.drop_all(engine)
    # 创建表
    Base.metadata.create_all(engine)
    # test_db()
    pass
