# -*- coding: utf-8 -*-
# @Time    : 2018/8/15 18:00
# @Author  : XiZhi
# @File    : main.py
import os
import sys
from scrapy.cmdline import execute

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# execute(["scrapy", "crawl", "aegis"])
# execute(["scrapy", "crawl", "aeg"])
execute(["scrapy", "crawl", "aegs"])