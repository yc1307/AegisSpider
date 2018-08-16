# -*- coding: utf-8 -*-
import json

import os

import redis
import scrapy
import time
import pymongo
import sys

from AegisSpider.items import AegisspiderItem, AegisrelatedItem


class AegsSpider(scrapy.Spider):
    name = 'aegs'
    date_stamp = time.time()
    date_stamp = int(date_stamp)  # 实时更新请求头中的时间戳
    allowed_domains = ['h5.law.push.aegis-info.com']
    start_urls = ['https://h5.law.push.aegis-info.com/law_api/api/law_inference/robot_multi_new']
    question = '如何在电子商务平台上进行知识产权侵权投诉？'
    headers = {
        'Host': 'h5.law.push.aegis-info.com',
        'Connection': 'keep-alive',
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://h5.law.push.aegis-info.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36 MicroMessenger/6.5.2.501 NetType/WIFI WindowsWechat QBCore/3.43.901.400 QQBrowser/9.0.2524.400',
        'Referer': 'https://h5.law.push.aegis-info.com/html/qavoice.html?id=1090&homestamp=' + str(
            date_stamp) + '000&openid=null',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.8,en-us;q=0.6,en;q=0.5;q=0.4'
    }
    formdata = {
        'content': question,
        'flag': '1',
        'qid': '1',
        'industry_ids': '1',
        'events_ids': '1090',
        'userid': 'h5_oCmhhxLW9jS95q8_VvQrScvLhc14',
        'case_cause_id': '0',
        'context': '{}',
        'sxcid': '',
        'sxdid': ''
    }

    def start_requests(self):
        '''爬虫起始点'''
        question_list = ['电子商务', '房屋买卖', '房屋租赁', '分家析产', '公司业务', '行政纠纷', '合伙联营', '合同纠纷', '婚姻家事', '继承', '家暴纠纷', '交通事故', '借贷纠纷', '劳动纠纷', '流程', '侵权纠纷', '侵权纠纷', '涉外商事', '物权纠纷', '物业纠纷', '相邻关系', '消费纠纷', '医患纠纷', '征地拆迁', '知识产权']
        for question in question_list:
            init_q_list = self.Query_prepare(domain=question)
            for question in init_q_list:
                self.formdata['content'] = question
                formdata = self.formdata
                yield scrapy.FormRequest(
                    url='https://h5.law.push.aegis-info.com/law_api/api/law_inference/robot_multi_new',
                    headers=self.headers,
                    method='POST',
                    formdata=formdata,
                    callback=self.parse,
                    meta={'question': formdata['content']},
                    errback=self.error_handle
                )

    def Query_prepare(self, domain):
        file_path = os.path.join(
            os.path.dirname(__file__), f'../question/{domain}.txt')
        if os.path.isfile(file_path):
            with open(file_path, encoding='utf8') as f:
                init_q_list = [i.strip() for i in f.readlines()]
        else:
            print('未发现案由关键词文件！')
            init_q_list = []

        return init_q_list

    def parse(self, response):
        '''处理问题详情页'''
        question = response.meta['question']
        html_str = json.loads(response.text)
        print(html_str)
        item = AegisspiderItem()
        item['question'] = question
        item['content'] = html_str
        # 对返回数据做处理
        data = html_str['data']

        if 'similar_question' in data:
            for new_qestion in data['similar_question']:
                self.formdata['content'] = new_qestion
                formdata = self.formdata
                yield scrapy.FormRequest(
                    url='https://h5.law.push.aegis-info.com/law_api/api/law_inference/robot_multi_new',
                    headers=self.headers,
                    method='POST',
                    formdata=formdata,
                    callback=self.parse,
                    meta={'question': formdata['content']},
                    errback=self.error_handle
                )
        yield item
        # if 'standardanswer' in data:
        #     item = AegisspiderItem()
        #     item['question'] = question
        #     item['standardanswer'] = data['standardanswer']
        #     item['content'] = html_str
        #     if 'laws' in data:
        #         item['laws'] = data['laws']
        # else:
        #     item = AegisspiderItem()
        #     item['question'] = question
        #     item['answer'] = data['answer']
        #     item['content'] = html_str
        #     if 'laws' in data:
        #         item['laws'] = data['laws']
        #     yield item

    def error_handle(self, response):
        print('程序出错')


