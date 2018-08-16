# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from pymongo import MongoClient
from scrapy.conf import settings

from AegisSpider.items import AegisspiderItem, AegisrelatedItem


class AegisspiderPipeline(object):
    def process_item(self, item, spider):
        return item


class AegisMongoDBPipeline(object):
    def open_spider(self, spider):
        self.client = MongoClient(
            host=settings['MONGDB_HOST'],
            port=settings['MONGODB_PORT']
        )
        self.db = self.client[settings['MONGODB_DBNAME']]
        self.collection = self.db[settings['MONGODB_COL_RELATED']]
        # 由于不能同时开启多个,使用isinstance进行判断

    def process_item(self, item, spider):
        if isinstance(item, AegisrelatedItem):
            answer_infos = dict(item)
            self.collection.insert(answer_infos)
        if isinstance(item, AegisspiderItem):
            related_infos = dict(item)
            self.collection = self.db[settings['MONGODB_COL_ANSER']]
            self.collection.insert(related_infos)
        return item


