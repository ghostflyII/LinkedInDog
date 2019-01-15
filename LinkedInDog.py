# -*- coding: utf-8 -*-
"""
用于自动化保存领英个人简介
可通过领英搜索页和百度搜索页爬取
"""

import pyautogui
import time
import csv
import re
import time
from lxml import etree
import requests
from urllib import quote
import urllib
import click
from selenium import webdriver
from selenium.common.exceptions import WebDriverException

LOGIN_URL='https://www.linkedin.com/'


class InvalidUserException(Exception):
    pass


class InvalidBrowserException(Exception):
    pass


class WebBrowser(object):

    def __init__(self, browser,profile_path):
        self.browser = browser
        self.driver = None
        self.profile = profile_path

    def __enter__(self):
        if self.browser.lower() == 'firefox':
            if self.profile != None:
                BrowserProfile=webdriver.FirefoxProfile(self.profile)
                self.driver = webdriver.Firefox(BrowserProfile)
            else:
                self.driver = webdriver.Firefox()
        elif self.browser.lower() == 'chrome':
            if self.profile != None:
                option = webdriver.ChromeOptions()
                option.add_argument('--user-data-dir='+self.profile)
                self.driver = webdriver.Chrome(option)
            else:
                self.driver = webdriver.Chrome()
        else:
            raise InvalidBrowserException("未知的浏览器")

        return self

    def __exit__(self, _type, value, traceback):
        if _type is OSError or _type is WebDriverException:
            click.echo("您没有安装该浏览器")
            return False
        if _type is InvalidBrowserException:
            click.echo("只能使用Firefox和Chrome")
            return False

        self.driver.close()

def SaveAsAction():
    """
    另存为操作
    end用于加载更多
    """

    time.sleep(10)
    pyautogui.hotkey('end')
    time.sleep(2)
    pyautogui.hotkey('ctrl', 's')
    time.sleep(5)
    pyautogui.hotkey('enter')
    time.sleep(3)


def login(driver, username,password):

    driver.get(LOGIN_URL)
    userfield = driver.find_element_by_id('login-email')
    passfield = driver.find_element_by_id('login-password')
    submit_form = driver.find_element_by_id('login-submit')

    if userfield and passfield:
        userfield.send_keys(username)
        passfield.send_keys(password)
        submit_form.submit()
        click.echo("领英登录成功")
        time.sleep(1.5)


def get_linkedin_url(url):
    """ 百度搜索出来的是百度跳转链接，要从中提取出linkedin链接 """
    try:
        r = requests.get(url, allow_redirects=False)
        if 'linkedin.com/in/' in r.headers['Location']:
            return r.headers['Location']
    except Exception, e:
        print '百度获取领英链接失败: %s' % url
    return ''

def Baidu(num,keywords):
    """ 百度搜索最多76页 """
    Baiduurl=[]
    if num > 76:
        num=76
    searchurl = 'http://www.baidu.com/s?ie=UTF-8&wd=%20%7C%20领英%20' + quote(keywords) + '%20site%3Alinkedin.com'
    failed_time=0
    while len(searchurl)>0 and failed_time<10:
        try:
            r = requests.get(searchurl, timeout=10)
        except:
            failed_time += 1
            continue
        if r.status_code == 200:
            for url in re.findall('"(http://www\.baidu\.com/link\?url=.*?)"', r.content):  # 一页有10个搜索结果
                url=get_linkedin_url(url)
                if url not in Baiduurl:
                    Baiduurl.append(url)
            tree = etree.HTML(r.content)
            nextpage_txt = tree.xpath(
                '//div[@id="page"]/a[@class="n" and contains(text(), "下一页")]/@href'.decode('utf8'))
            searchurl = 'http://www.baidu.com' + nextpage_txt[0].strip() if nextpage_txt else ''
            failed_time = 0
            num -= 1
            if num <= 0:
                break
        else:
            failed_time += 1
            print '领英搜索失败: %s' % r.status_code
    Baiduurl.remove('')
    return Baiduurl

def showmore(driver):
    try:
        for button in driver.find_elements_by_xpath(
                "//button[@class='pv-profile-section__see-more-inline pv-profile-section__text-truncate-toggle link']"):
            button.click()
    except:
        pass
    try:
        for button in driver.find_elements_by_xpath(
                "//button[@class='pv-profile-section__card-action-bar pv-skills-section__additional-skills artdeco-container-card-action-bar']"):
            button.click()
    except:
        pass
    try:
        for button in drive.find_elements_by_xpath(
                "//button[@class='pv-top-card-section__summary-toggle-button pv-profile-section__card-action-bar artdeco-container-card-action-bar mt4']"):
            button.click()
    except:
        pass

@click.group()
def spider():
    pass


@click.command()
@click.option('--user',  help='Your linkedIn username')
@click.option('--pwd', help='Your linkedIn password')
@click.option('--keywords',help='name, company...')
@click.option('--browser', default='firefox', help='Browser to run with')
@click.option('--profile', default=None, help='The current profile of your browser')
@click.option('--sources', default=0, type=int, help='0: Only linkedIn\n1: Only Baidu\n2: Add Baidu')
@click.option('--linkedinnum', default=1, type=int, help='Number of linkedin search pages')
@click.option('--num', default=1, type=int, help='Number of Baidu search pages')
def crawl(browser, profile, user, pwd, sources, num, keywords,linkedinnum):
    with WebBrowser(browser,profile) as Browser:
        login(Browser.driver, user,pwd)

        Baiduurls=Baidu(num,keywords) if sources !=0 else []
        if len(Baiduurls) >0 and sources == 1:
            for link in Baiduurls:
                Browser.driver.get(link)
                print link
                showmore(Browser.driver)
                SaveAsAction()
        if sources == 0 or sources == 2:
            linked_num=linkedinnum
            linkedin_url='https://www.linkedin.com/search/results/people/?keywords='+quote(keywords)+'&origin=SUGGESTION'+'&page='+str(linked_num)
            while linked_num>0:
                Browser.driver.get(linkedin_url)
                all_link = Browser.driver.find_elements_by_xpath("//div[@class='search-result__image-wrapper']/a[@class='search-result__result-link ember-view']")
                links=[link.get_attribute('href') for link in all_link]
                for link in links:
                    Browser.driver.get(link)
                    print link
                    showmore(Browser.driver)
                    SaveAsAction()
                linked_num -=1
                linkedin_url = 'https://www.linkedin.com/search/results/people/?keywords=' + quote(keywords) + '&origin=SUGGESTION' + '&page=' + str(linked_num)
            if sources == 2:
                for link in Baiduurls:
                    Browser.driver.get(link)
                    print link
                    showmore(Browser.driver)
                    SaveAsAction()



spider.add_command(crawl)


if __name__ == '__main__':
    spider()
