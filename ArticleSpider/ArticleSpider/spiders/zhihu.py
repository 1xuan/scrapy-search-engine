# -*- coding: utf-8 -*-
import scrapy
from ArticleSpider.utils.zhihu_login import ZhihuAccount

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

    def parse(self, response):
        pass

    def start_requests(self):
        return [scrapy.Request('https://www.zhihu.com/signup?next=%2F', headers=HEADERS, callback=self.login)]

    def login(self, response):
        account = ZhihuAccount()
        ret = account.login(username='13108169041', password='zh951103', load_cookies=True)
        if ret:
            for url in self.start_urls:
                rep = account.get_page(url)
                yield self.parse(rep)




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


