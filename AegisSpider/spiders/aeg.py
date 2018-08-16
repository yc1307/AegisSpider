# -*- coding: utf-8 -*-
import json

import os

import requests
import scrapy


class AegSpider(scrapy.Spider):
    name = 'aeg'
    allowed_domains = ['h5.law.push.aegis-info.com']
    start_urls = ['https://h5.law.push.aegis-info.com/']
    headers = {
        'Host': 'h5.law.push.aegis-info.com',
        'Connection': 'keep-alive',
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://h5.law.push.aegis-info.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36 MicroMessenger/6.5.2.501 NetType/WIFI WindowsWechat QBCore/3.43.901.400 QQBrowser/9.0.2524.400',
        'Referer': 'https://h5.law.push.aegis-info.com/html/qavoice.html?id=1090&homestamp=1534385806000&openid=null',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.8,en-us;q=0.6,en;q=0.5;q=0.4',
    }

    def __init__(self, user_id='h5_oCmhhxNzpGkYdzgEky453_b5iZnI'):
        self.user_id = user_id
        self.session = self.__init_session()
        self.curdir = os.path.dirname(__file__)

    def __init_session(self):
        s = requests.Session()
        s.headers.update(self.headers)
        return s

    def post_content(self, content, qid='1', flag=1, case_cause_id=0):
        '''提交内容并获取答案'''
        url = 'https://h5.law.push.aegis-info.com/server_8886/qa'
        data = json.dumps({
            'content': content,
            'flag': flag,
            'qid': qid,
            'industry_ids': 1,
            'events_ids': '1124',
            'userid': self.user_id,
            'case_cause_id': case_cause_id,
            'context': r'{}'
        })
        try:
            res = self.session.post(url, data=data, timeout=10)
            res.raise_for_status()
        except Exception as e:
            print('获取答案失败', e)
            return
        res = res.json().get('data')
        return res

    def get_result(self, question):
        '''处理返回的数据'''
        result = {}
        result['question'] = question
        result['related'] = self.get_related(question)
        data = self.post_content(question)
        if not data:
            if result['related']:
                yield result
            return
        status_code = data.get('type')
        if status_code == 110:
            if data.get('useful') or not data.get('flag_for_web'):
                result['answer'] = data['answer']
                yield result
            else:
                yield
        elif status_code == 120:
            yield
        elif status_code == 130:
            result['answer'] = data['answer']
            if data.get('laws'):
                result['laws'] = data.get('laws')
            pics = data['pictures']
            url = data['url']
            result['attachment'] = []
            # for pic in pics:
            #     attachment = self.get_attachment(url, pic)
            #     if attachment:
            #         path = os.path.join(self.curdir, 'pics', pic)
            #         result['attachment'].append(path)
            #         if not os.path.isfile(path):
            #             with open(path, 'wb') as f:
            #                 f.write(attachment)
            yield result
        elif status_code == 140:
            result['answer'] = data['answer']
            if data.get('laws'):
                result['laws'] = data.get('laws')
            yield result
        elif status_code == 151:
            result['related'].extend(data['similar_question'])
            yield result
        elif status_code == 152:
            sub_question = data['answer']
            choices = data['choices']
            qid = data['qid']
            options = []
            result_ = result.copy()
            for choice in choices:
                title = choice['title']
                content = choice['qid']
                options.append([sub_question, title])
                for opt, res in self.handle_interactive_dialogue(content, qid):
                    result_['options'] = options + opt
                    result_.update(res)
                    yield result_
                    result_ = result.copy()
                options = []
        elif status_code == 154:
            sub_question = data['answer']
            tags = data['tags']
            qid = data['qid']
            case_cause_id = data.get('case_cause_id', 0)
            options = []
            result_ = result.copy()
            for tag in tags:
                title = tag['zhName']
                content = tag['enName']
                type_code = tag['type']
                flag = [4, 5][int(type_code)]
                options.append([sub_question, title])
                for opt, res in self.handle_interactive_report(content, qid, flag, case_cause_id):
                    result_['options'] = options + opt
                    result_.update(res)
                    yield result_
                    result_ = result.copy()
                options = []
        else:
            print('未知情况')
            yield

    def handle_interactive_report(self, content, qid, flag, case_cause_id):
        '''处理有交互的报告
        类似交互问题，遍历并返回最终报告
        :param content: 选项的qid
        :param qid: 本轮对话的qid
        '''
        stop_criterion = set()

        def traversal(content, qid, flag, case_cause_id):
            '''遍历问题树'''
            nonlocal stop_criterion
            data = self.post_content(content, qid, flag, case_cause_id)
            if data.get('tags'):
                case_cause_id = data.get('case_cause_id', 0)
                answer = data['answer']
                tags = data['tags']
                for tag in tags:
                    title = tag['zhName']
                    content = tag['enName']
                    if title in stop_criterion:
                        continue
                    stop_criterion.add(title)
                    type_code = tag['type']
                    flag = [4, 5][int(type_code)]
                    yield [answer, title]
                    yield from traversal(content, qid, flag, case_cause_id)
            else:
                yield data

        items = traversal(content, qid, flag, case_cause_id)
        pointer = []
        option = []
        for item in items:
            if isinstance(item, list):
                if item[0] not in pointer:
                    pointer.append(item[0])
                    option.append(item)
                else:
                    idx = pointer.index(item[0])
                    pointer = pointer[:idx]
                    option = option[:idx]
                    pointer.append(item[0])
                    option.append(item)
            else:
                result = {}
                status_code = item.get('type')
                if status_code == 560:
                    laws = item.get('laws')
                    if laws:
                        result['laws'] = item.get('laws')
                    result['answer'] = item['answer']
                else:
                    result['answer'] = ''
                yield option, result

    def handle_interactive_dialogue(self, content, qid, flag=2):
        '''处理有交互情况
        遍历问题树并返回路径及回答
        :param content: 选项的qid
        :param qid: 本轮对话的qid
        :param flag: 交互问答的flag都是2 交互报告根据结果不同flag不同
        '''
        stop_criterion = set()

        def traversal(content, qid, flag):
            '''遍历问题树'''
            nonlocal stop_criterion
            data = self.post_content(content, qid, flag)
            if data.get('choices'):
                sub_question = data['answer']
                choices = data['choices']
                for choice in choices:
                    title = choice['title']
                    content = choice['qid']
                    if title in stop_criterion:
                        continue
                    stop_criterion.add(title)
                    yield [sub_question, title]
                    yield from traversal(content, qid, flag)
            else:
                yield data

        items = traversal(content, qid, flag)
        pointer = []
        option = []
        for item in items:
            if isinstance(item, list):
                if item[0] not in pointer:
                    pointer.append(item[0])
                    option.append(item)
                else:
                    idx = pointer.index(item[0])
                    pointer = pointer[:idx]
                    option = option[:idx]
                    pointer.append(item[0])
                    option.append(item)
            else:
                result = {}
                status_code = item.get('type')
                if status_code == 210:
                    result['answer'] = item['answer']
                elif status_code == 230:
                    result['answer'] = item['answer']
                    if item.get('laws'):
                        result['laws'] = item.get('laws')
                    pics = item['pictures']
                    url = item['url']
                    result['attachment'] = []
                    # for pic in pics:
                    #     attachment = self.get_attachment(url, pic)
                    #     if attachment:
                    #         path = os.path.join(self.curdir, 'pics', pic)
                    #         result['attachment'].append(path)
                    #         if not os.path.isfile(path):
                    #             with open(path, 'wb') as f:
                    #                 f.write(attachment)
                elif status_code == 260:
                    result['answer'] = item['answer']
                    if item.get('laws'):
                        result['laws'] = item.get('laws')
                else:
                    result['answer'] = ''
                    print(item, end='\n\n', file=open('log.txt', 'w', encoding='utf8'))
                yield option, result

    def get_related(self, content):
        '''获取相关问题'''
        url = 'https://h5.law.push.aegis-info.com/server_8881/qa/completion'
        payload = {'key': content}
        try:
            res = self.session.get(url, params=payload, timeout=10)
            res.raise_for_status()
        except Exception as e:
            print('获取答案失败', e)
            return []
        data = res.json().get('data')
        if data:
            related = [i['text'] for i in data]
            if content in related:
                related.remove(content)
            return related
        return []

    def start_requests(self):
        urls = ['https://h5.law.push.aegis-info.com/server_8881/qacompletion?key=起诉了能查封欠钱人的房子吗？']
        for i, url in enumerate(urls, 1):
            yield scrapy.Request(url, meta={'cookiejar': i}, callback=self.parse)

    def parse(self, response):

        return scrapy.FormRequest(
            url='https://h5.law.push.aegis-info.com/server_8881/qacompletion?key={question}'.format(question='起诉了能查封欠钱人的房子吗？'),
            data=json.dumps({
                'flag': 1,
                'qid': '1',
                'industry_ids': 1,
                'events_ids': '1124',
                'userid': self.user_id,
                'case_cause_id': 0,
            })
        )
        # print(response.text)
        # self.get_result('起诉了能查封欠钱人的房子吗？')
