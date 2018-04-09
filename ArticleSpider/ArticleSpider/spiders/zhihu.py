# -*- coding: utf-8 -*-
import re
import json
import datetime

from urllib import parse
import scrapy
import requests
from scrapy.loader import ItemLoader

from ArticleSpider.utils.zhihu_login import ZhihuAccount
from ..items import ZhihuAnswerItem, ZhihuQuestionItem

HEADERS = {
    'Connection': 'keep-alive',
    'Host': 'www.zhihu.com',
    'Referer': 'https://www.zhihu.com/',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/56.0.2924.87 Mobile Safari/537.36'
    }
LOGIN_URL = 'https://www.zhihu.com/signup'
LOGIN_API = 'https://www.zhihu.com/api/v3/oauth/sign_in'
FORM_DATA = {
    'client_id': 'c3cef7c66a1843f8b3a9e6a1e3160e20',
    'grant_type': 'password',
    'source': 'com.zhihu.web',
    'username': '',
    'password': '',
    # 改为'cn'是倒立汉字验证码
    'lang': 'cn',
    'ref_source': 'homepage'
}


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']

    # question的answer第一页请求
    start_answer_url = "http://www.zhihu.com/api/v4/questions/{0}/answers?include=data%5B%2A%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info%2Cquestion%2Cexcerpt%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cupvoted_followees%3Bdata%5B%2A%5D.mark_infos%5B%2A%5D.url%3Bdata%5B%2A%5D.author.follower_count%2Cbadge%5B%3F%28type%3Dbest_answerer%29%5D.topics&limit={1}&offset={2}&sort_by=default"

    def parse(self, response):
        """
        提取出html页面中的所有url， 并跟踪这也url进一步爬取
        如果提取的url中格式为/question/xxx， 就下载之后直接进入解析
        :param response:
        :return:
        """
        all_urls = response.xpath('//*/@href').extract()
        all_urls = [parse.urljoin(response.url, url) for url in all_urls]
        all_urls = filter(lambda x: True if x.startswith('https') else False, all_urls)
        for url in all_urls:
            match_obj = re.match(r"(.*?zhihu.com/question/(\d+))(/|$).*", url)
            if match_obj:
                # 如果提取到question相关页面， 则调用parse_question处理
                request_url = match_obj.group(1)
                yield scrapy.Request(request_url, headers=self.account.session.headers, cookies=requests.utils.dict_from_cookiejar(self.account.session.cookies), callback=self.parse_question)
            else:
                # 如果没有提取到question相关页面， 则进一步跟踪
                yield scrapy.Request(url, headers=self.account.session.headers,
                                     cookies=requests.utils.dict_from_cookiejar(self.account.session.cookies),
                                     callback=self.parse)


    def parse_question(self, response):
        # 处理question页面，从页面中提取出具体的question item
        item_loader = ItemLoader(item=ZhihuQuestionItem(), response=response)
        item_loader.add_xpath('title', '//div[@class="QuestionHeader-title"]/a/text()')
        item_loader.add_xpath('content', '//span[@itemprop="text"]/text()')
        item_loader.add_value('url', response.url)

        match_obj = re.match(r"(.*?zhihu.com/question/(\d+))(/|$).*", response.url)
        if match_obj:
            question_id = int(match_obj.group(2))

        item_loader.add_value('zhihu_id', question_id)
        item_loader.add_xpath('answer_num', '//h4[@class="List-headerText"]/span/text()')
        item_loader.add_xpath('watch_user_num', '//main[@role="main"]/div[1]/meta[@itemprop="zhihu:followerCount"]/@content')
        item_loader.add_xpath('topics', '//main[@role="main"]/div[1]/meta[@itemprop="keywords"]/@content')

        question_item = item_loader.load_item()

        yield scrapy.Request(self.start_answer_url.format(question_id, 20, 0), headers=self.account.session.headers, callback=self.parse_answer)
        yield question_item

    def parse_answer(self, response):
        # 处理question的answer
        ans_json = json.loads(response.text)
        is_end = ans_json['paging']['is_end']
        next_url = ans_json['paging']['next']

        # 提取answer的具体字段
        for answer in ans_json['data']:
            answer_item = ZhihuAnswerItem()
            answer_item['zhihu_id'] = answer['id']
            answer_item['url'] = answer['url']
            answer_item['question_id'] = answer['question']['id']
            answer_item['author_id'] = answer['author']['id'] if 'id' in answer['author'] else None
            answer_item['content'] = answer['content'] if 'content' in answer else None
            answer_item['parise_num'] = answer['voteup_count']
            answer_item['comments_num'] = answer['comment_count']
            answer_item['create_time'] = answer['created_time']
            answer_item['update_time'] = answer['updated_time']
            answer_item['crawl_time'] = datetime.datetime.now()

            yield answer_item

        if not is_end:
            yield scrapy.Request(next_url, headers=self.account.session.headers, callback=self.parse_answer)

    def start_requests(self):
        return [scrapy.Request('https://www.zhihu.com/signup?next=%2F', headers=HEADERS, callback=self.login)]

    def login(self, response):
        self.account = ZhihuAccount()
        ret = self.account.login(username='你的帐号', password='你的密码', load_cookies=True)
        if ret:
            for url in self.start_urls:
                yield scrapy.Request(url, dont_filter=True, headers=self.account.session.headers, cookies=requests.utils.dict_from_cookiejar(self.account.session.cookies), callback=self.parse)



    """
    把请求头部和表单信息交给scrapy去请求
    """
    # def login(self, response):
    #
    #     post_url = 'https://www.zhihu.com/api/v3/oauth/sign_in'
    #     xsrf = self.get_token()
    #     self.session = requests.session()
    #     self.session.headers = self.headers.copy()
    #     self.session.headers.update({
    #         'authorization': 'oauth c3cef7c66a1843f8b3a9e6a1e3160e20',
    #         'X-Xsrftoken': xsrf,
    #     })
    #
    #     timestamp = str(int(time.time() * 1000))
    #
    #     self.post_data = self.form_data.copy()
    #
    #     self.post_data.update({
    #         'captcha': self.get_captcha(self.session.headers),
    #         'timestamp': timestamp,
    #         'signature': self.get_signature(timestamp)
    #     })
    #
    #     return [scrapy.FormRequest(
    #         url=post_url,
    #         formdata=self.post_data,
    #         headers=self.session.headers,
    #         callback=self.check_login,
    #     )]


