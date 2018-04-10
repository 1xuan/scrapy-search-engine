# -*- coding: utf-8 -*-
import scrapy


class BaiduSpider(scrapy.Spider):
    name = 'baidu'
    allowed_domains = ['www.lagou.com']
    start_urls = ['https://www.lagou.com/']

    def parse(self, response):
        pass
