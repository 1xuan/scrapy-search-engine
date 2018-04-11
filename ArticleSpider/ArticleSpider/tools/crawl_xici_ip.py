__author__ = 'yixuan'
__date__ = '上午10:50'
import requests
from scrapy.selector import Selector
import MySQLdb

conn = MySQLdb.connect(host='127.0.0.1', user='root', passwd='123456', db='article_spider', charset='utf8')
cursor = conn.cursor()


def crawl_ips():
    # 爬取西刺的免费代理ip
    headers = {'User-Agent': "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Mobile Safari/537.36"}
    for i in range(500):
        re = requests.get("http://www.xicidaili.com/nn/{0}".format(i), headers=headers)

        selector = Selector(text=re.text)
        all_trs = selector.xpath('//table/tr[@class]')

        ip_list = []
        for tr in all_trs:
            speed_str = tr.xpath('td[7]/div/@title').extract_first()
            if speed_str:
                speed = float(speed_str.split('秒')[0])

            all_texts = tr.xpath('td/text()').extract()
            ip = all_texts[0]
            port = all_texts[1]
            proxy_type = all_texts[5]
            ip_list.append((ip, port, proxy_type, speed))

        for ip_info in ip_list:
            cursor.execute(
                "insert proxy_ip(ip, port, speed, proxy_type) VALUES('{0}', '{1}', {2}, 'HTTP')".format(ip_info[0], ip_info[1], ip_info[3])
            )
            conn.commit()


class GetIP(object):
    def delete_ip(self, ip):
        delete_sql = """
            delete from proxy_ip where ip='{0}'
        """.format(ip)
        cursor.execute(delete_sql)
        conn.commit()
        return True

    def judge_ip(self, ip, port):
        # 判断ip是否可用
        http_url = "http://www.baidu.com"
        proxy_url = "http://{0}:{1}".format(ip, port)
        try:
            proxy_dict = {
                "http": proxy_url,
            }
            response = requests.get(http_url, proxies=proxy_dict)
        except Exception as e:
            print("invalid ip and port")
            self.delete_ip(ip)
            return False
        else:
            code = response.status_code
            if code >=200 and code < 300:
                print("effective ip")
            else:
                print("invalid ip and port")
                self.delete_ip(ip)
                return False

    def get_random_ip(self):
        # 从数据库中随机获取一个可用的ip
        sql = """
            SELECT ip, port FROM proxy_ip ORDER BY RAND() LIMIT 1
        """
        result = cursor.execute(sql)
        for ip_info in cursor.fetchall():
            ip = ip_info[0]
            port = ip_info[1]

            judge_re = self.judge_ip(ip, port)
            # if judge_re:
            #     return "http://{0}:{1}".format(ip, port)
            # else:
            #     return self.get_random_ip()

# print(crawl_ips())


if __name__ == '__main__':
    get_ip = GetIP()
    get_ip.get_random_ip()