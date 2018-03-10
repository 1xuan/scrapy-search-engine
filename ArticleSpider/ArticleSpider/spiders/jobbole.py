# -*- coding: utf-8 -*-
import scrapy


class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/']

    def parse(self, response):
        title = response.xpath('//div[@class="entry-header"]/h1/text()').extract()
        create_date = response.xpath('//p[@class="entry-meta-hide-on-mobile"]/text()').extract()[0].strip().replace(' ·', '')
        fav_nums = response.xpath('//div[@class="post-adds"]/span[2]/h10/text()').extract_first()
        comment_nums = response.xpath('//a[@href="#article-comment"]/h10/text()').extract()
        content = response.xpath('//div[@class="entry"]').extract()[0]
        tag_list = response.xpath('//div[@class="entry-meta"]/p/a/text()').extract()
        tags = ','.join(tag_list)
        pass

