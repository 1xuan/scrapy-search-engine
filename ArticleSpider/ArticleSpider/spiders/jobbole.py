# -*- coding: utf-8 -*-
import re
import scrapy
import datetime
from scrapy.http import Request
from urllib import parse
from scrapy.loader import ItemLoader
from selenium import webdriver
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals


from ArticleSpider.items import JobboleArticleItem, ArticleItemLoader
from ArticleSpider.utils.common import get_md5


class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    """
    集成selenium到scrapy
    """
    # def __init__(self):
    #     self.browser = webdriver.Firefox()
    #     super(JobboleSpider, self).__init__()
    #     dispatcher.connect(self.spider_closed, signals.spider_closed)
    #
    # def spider_closed(self, spider):
    #     # 当爬虫停止时退出browser
    #     print("spider closed")
    #     self.browser.quit()

    # 收集jobbole所有404url以及404页面
    # handle_httpstatus_list = [404]
    #
    # def __init__(self):
    #     self.fail_ulrs = []
    #     dispatcher.connect(self.handle_spider_closed, signals.spider_closed)
    #
    # def handle_spider_closed(self, spider, reason):
    #     self.crawler.stats.set_value("failed_urls", ",".join(self.fail_ulrs))
    #     pass

    def parse(self, response):
        # if response.status == 404:
        #     self.fail_ulrs.append(response.url)
        #     self.crawler.stats.inc_value("failed_url")

        # 解析列表页中的所有文章url并交给scrapy下载后并进行解析
        post_nodes = response.xpath('//div[@class="post-thumb"]')
        for post_node in post_nodes:
            image_url = post_node.xpath('./a/img/@src').extract_first()
            post_url = post_node.xpath('./a/@href').extract_first()
            yield Request(url=parse.urljoin(response.url, post_url), meta={'front_image_url': parse.urljoin(response.url, image_url)}, callback=self.parse_detail)

        # 获取下一页的url并交给scrapy进行下载
        next_url = response.xpath('//a[@class="next page-numbers"]/@href').extract_first()
        if next_url:
            yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse_detail)

    def parse_detail(self, response):
        # article_item = JobboleArticleItem()

        # 提取文章的具体字段
        # front_image_url = response.meta.get("front_image_url", "")     # 文章封面图
        # title = response.xpath('//div[@class="entry-header"]/h1/text()').extract_first()
        # create_date = response.xpath('//p[@class="entry-meta-hide-on-mobile"]/text()').extract()[0].strip().replace(' ·', '')
        # fav_nums = response.xpath('//div[@class="post-adds"]/span[2]/h10/text()').extract_first()
        # comment_nums = response.xpath('//a[@href="#article-comment"]/span/text()').extract_first()
        # content = response.xpath('//div[@class="entry"]').extract()[0]
        # tag_list = response.xpath('//div[@class="entry-meta"]/p/a/text()').extract()
        # tag_list = [element for element in tag_list if not element.strip().endswith('评论')]
        # tags = ','.join(tag_list)
        #
        # article_item['url_object_id'] = get_md5(response.url)
        # article_item['title'] = title
        # article_item['url'] = response.url
        # article_item['create_date'] = create_date
        # article_item['front_image_url'] = [front_image_url]
        # article_item['comment_nums'] = comment_nums
        # article_item['fav_nums'] = fav_nums
        # article_item['tags'] = tags
        # article_item['content'] = content


        # 通过ItemLoader加载item
        item_loader = ArticleItemLoader(item=JobboleArticleItem(), response=response)
        item_loader.add_xpath('title', '//div[@class="entry-header"]/h1/text()')
        item_loader.add_value('url', response.url)
        item_loader.add_value('url_object_id', get_md5(response.url))
        item_loader.add_xpath('create_date', '//p[@class="entry-meta-hide-on-mobile"]/text()')

        front_image_url = response.meta.get("front_image_url", "")
        item_loader.add_value('front_image_url', [front_image_url])

        item_loader.add_xpath('comment_nums', '//a[@href="#article-comment"]/span/text()')

        fav_nums = response.xpath('//div[@class="post-adds"]/span[2]/h10/text()').extract_first()

        if fav_nums is None:
            fav_nums = '0'
        item_loader.add_value('fav_nums', fav_nums)

        item_loader.add_xpath('tags', '//div[@class="entry-meta"]/p/a/text()')
        item_loader.add_xpath('content', '//div[@class="entry"]')

        article_item = item_loader.load_item()

        yield article_item

