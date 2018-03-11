# -*- coding: utf-8 -*-
import re
import scrapy
from scrapy.http import Request
from urllib import parse


class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):
        """
        1.获取文章列表页中的文章url并交给scrapy下载后并进行解析
        2.获取下一页的url并交给scrapy进行下载，下载完成后交给parse
        :param response:
        :return:
        """
        # 解析列表页中的所有文章url并交给scrapy下载后并进行解析
        post_urls = response.xpath('//a[@class="archive-title"]/@href').extract()
        for post_url in post_urls:
            yield Request(url=parse.urljoin(response.url, post_url), callback=self.parse_detail)

        # 获取下一页的url并交给scrapy进行下载
        next_url = response.xpath('//a[@class="next page-numbers"]/@href').extract_first()
        if next_url:
            yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse_detail)

    def parse_detail(self, response):
        # 提取文章的具体字段
        title = response.xpath('//div[@class="entry-header"]/h1/text()').extract_first()
        create_date = response.xpath('//p[@class="entry-meta-hide-on-mobile"]/text()').extract()[0].strip().replace(' ·', '')
        fav_nums = response.xpath('//div[@class="post-adds"]/span[2]/h10/text()').extract_first()
        comment_nums = response.xpath('//a[@href="#article-comment"]/span/text()').extract_first()
        match_re = re.match('.*?(\d+).*', comment_nums)
        if match_re:
            comment_nums = int(match_re.group(1))
        else:
            comment_nums = 0
        content = response.xpath('//div[@class="entry"]').extract()[0]
        tag_list = response.xpath('//div[@class="entry-meta"]/p/a/text()').extract()
        tag_list = [element for element in tag_list if not element.strip().endswith('评论')]
        tags = ','.join(tag_list)
        scrapy.Request
        pass

6