# -*- coding: utf-8 -*-
import json
import os
import scrapy
import requests
import time
from scrapy.conf import settings


class AegisSpider(scrapy.Spider):
    name = 'aegis'
    allowed_domains = ['h5.law.push.aegis-info.com']
    start_urls = ['http://h5.law.push.aegis-info.com/']
    date_stamp = time.time()
    date_stamp = int(date_stamp)
    headers = {
        'Host': 'h5.law.push.aegis-info.com',
        'Connection': 'keep-alive',
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://h5.law.push.aegis-info.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36 MicroMessenger/6.5.2.501 NetType/WIFI WindowsWechat QBCore/3.43.901.400 QQBrowser/9.0.2524.400',
        'Referer': 'https://h5.law.push.aegis-info.com/html/qavoice.html?id=1090&homestamp={1534385806000&openid=null',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.8,en-us;q=0.6,en;q=0.5;q=0.4',
    }

    def start_requests(self):
        question_list = ['电子商务', '房屋买卖', '房屋租赁', '分家析产', '公司业务', '行政纠纷', '合伙联营', '合同纠纷', '婚姻家事', '继承', '家暴纠纷', '交通事故', '借贷纠纷', '劳动纠纷', '流程', '侵权纠纷', '侵权纠纷', '涉外商事', '物权纠纷', '物业纠纷', '相邻关系', '消费纠纷', '医患纠纷', '征地拆迁', '知识产权']
        for question in question_list:
            self.Query_prepare(domain=question)

            return scrapy.Request(
                url='https://h5.law.push.aegis-info.com/server_8881/qacompletion?key={question}'.format(question=question),
                method='POST',
                headers=self.headers,
                callback=self.parse
            )

    def parse(self, response):
        print(response.text)

    def Query_prepare(self, domain):
        file_path = os.path.join(
            os.path.dirname(__file__), f'../question/{domain}.txt')
        if os.path.isfile(file_path):
            with open(file_path, encoding='utf8') as f:
                init_q_list = [i.strip() for i in f.readlines()]
        else:
            print('未发现案由关键词文件！')
            init_q_list = []
        # ques_pool = QuesPool(new=new, seed=init_q_list)
        # collection = spider.db[domain]
        # question = ques_pool.pop()
        # while question:
        #     print(f'[Processing] {question}')
        #     if collection.count_documents({'question': question}):
        #         # 检查是否已存在
        #         print('\t已存在')
        #         question = ques_pool.pop()
        #         continue
        #     results = spider.get_result(question)
        #     for res in results:
        #         time.sleep(.5)
        #         if not res:
        #             continue
        #         related = res.get('related')
        #         if related:
        #             ques_pool.add(*related)
        #         else:
        #             res.pop('related')
        #         spider.to_mongodb(res, domain)
        #     question = ques_pool.pop()
        # else:
        #     spider.session.close()
        #     spider.client.close()
        #     print('done!')

