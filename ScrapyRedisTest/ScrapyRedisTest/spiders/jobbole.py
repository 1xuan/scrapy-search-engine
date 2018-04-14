__author__ = 'yixuan'
__date__ = '下午1:55'

from scrapy_redis.spiders import RedisSpider
from scrapy.http import Request
from urllib import parse


class MySpider(RedisSpider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    redis_key = "jobbole:start_urls"

    def parse(self, response):

        # 解析列表页中的所有文章url并交给scrapy下载后并进行解析
        post_nodes = response.xpath('//div[@class="post-thumb"]')
        for post_node in post_nodes:
            image_url = post_node.xpath('./a/img/@src').extract_first()
            post_url = post_node.xpath('./a/@href').extract_first()
            yield Request(url=parse.urljoin(response.url, post_url),
                          meta={'front_image_url': parse.urljoin(response.url, image_url)}, callback=self.parse_detail)

        # 获取下一页的url并交给scrapy进行下载
        next_url = response.xpath('//a[@class="next page-numbers"]/@href').extract_first()
        if next_url:
            yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse_detail)

    def parse_detail(self, response):

        pass
