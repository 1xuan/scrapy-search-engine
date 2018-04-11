__author__ = 'yixuan'
__date__ = '下午2:59'

from selenium import webdriver
from scrapy.selector import Selector

"""
无界面浏览器
"""
# from pyvirtualdisplay import Display
# display = Display(visible=0, size=(800, 600))
# display.start()

browser = webdriver.Firefox()

browser.get("http://39.108.224.191/")
print(browser.page_source)

"""
知乎登录
"""
# import time
# time.sleep(5)
#
# browser.find_element_by_xpath('//div[@class="SignContainer-switch"]/span').click()
# browser.find_element_by_xpath('//div[@class="SignFlow-accountInput Input-wrapper"]/input').send_keys("你的帐号")
# browser.find_element_by_xpath('//input[@name="password"]').send_keys("你的密码")
# browser.find_element_by_xpath('//button[@class="Button SignFlow-submitButton Button--primary Button--blue"]').click()
#
#
# print(browser.page_source)
# browser.quit()



