# -*- coding: utf-8 -*-
import re
import scrapy
from scrapy.http import Request
from urllib import parse

from ArticleSpider.items import JobboleArticleItem


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
        article_item = JobboleArticleItem()

        # 提取文章的具体字段
        front_image_url = response.meta.get("front_image_url", "")     # 文章封面图
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

        article_item['title'] = title
        article_item['url'] = response.url
        article_item['create_data'] = create_date
        article_item['front_image_url'] = [front_image_url]
        article_item['comment_nums'] = comment_nums
        article_item['fav_nums'] = fav_nums
        article_item['tags'] = tags
        article_item['content'] = content

        yield article_item

