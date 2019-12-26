import os
import re

import pymongo
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
# from webdriver_manager.firefox import GeckoDriverManager


import requests as req
from get_proxy import generate_proxy, gen_collection
from requests.exceptions import ProxyError


DEBUG=True

SEARCH_ENGINE = "https://www.google.co.in/search?q="
SCRAP_PAGE_COUNT = 10
SCRAP_RESULT_COUNT = 20

#path where the chromedriver is stored
SELENIUM_EXTENSION = os.path.join(".driver_extensions", "1.22.2_0")

XPATH = '//*[@id="hdtb-msb-vis"]/div[2]/a'



class SeleniumBrowser():

    def __init_selenium(self):
        try:
            proxy = generate_proxy(self.collector)

            #depening on the requirments, the browser settings may be changed

            # options = webdriver.ChromeOptions()
            # options.add_argument('--ignore-certificate-errors')
            # options.add_argument('--incognito')
            # options.add_argument('--headless')
            # options.add_argument('load-extension=' + SELENIUM_EXTENSION)
            # print(proxy)
            PROXY_SERVER = str(proxy.host) + ":" + str(proxy.port)
            print(PROXY_SERVER)
            # options.add_argument(
            #     '--proxy-server=%s' % PROXY_SERVER)
            # browser = webdriver.Chrome(
            #     ChromeDriverManager().install())
            caps = webdriver.DesiredCapabilities.HTMLUNIT.copy()
            caps['platform'] = "WINDOWS"
            caps['version'] = "10"
            # caps['proxy'] = {
            #     str(proxy.type) + "Proxy": PROXY_SERVER
            # }
            browser = webdriver.Remote(
                desired_capabilities=webdriver.DesiredCapabilities.HTMLUNIT)
            # browser = webdriver.Chrome(
            #     ChromeDriverManager().install())
            # browser.install_addon(SELENIUM_EXTENSION, temporary=True)
            return browser
        except:
            if DEBUG:
                raise
            

    def __init__(self, uid):
        self.collector, _ = gen_collection(uid)
        self.browser = self.__init_selenium()

    def __restart_selenium(self):
        self.browser.close()
        #self.browser = self.init_selenium(self.COLLECTOR)
        self.browser = self.__init_selenium()

    def __check_browser_connect(self, browser):
        """
        Checks if the browsers connection is correct or not
        """
        text = browser.text
        print(text)
        messages = ["might be temporarily down or it may have moved permanently to a new web address",
                    "There is something wrong with the proxy server, or the address is incorrect."]
        print(messages)
        return True

    def stop_selenium(self):
        self.browser.close()

    def connect(self, link, number_of_retries=3):
        browser = self.browser
        # browser = init_selenium(proxy.host + ":" + proxy.port)
        while number_of_retries:
            # Loop till a valid hit
            try:
                browser.get(link)
                # check if it returns correctly
                # if not check_browser_connect(browser):
                #     raise
                return browser
            except:
                self.__restart_selenium()
                number_of_retries -= 1
                continue
        # browser.close()
        return False


def generate_link_perpage(query, page_no, links, sbo):
    url = SEARCH_ENGINE + query + "&start=" + \
        str((page_no - 1) * 10) + "&tbm=nws"
    print(url)
    browser = sbo.connect(url, 5)
    if not browser:
        # no valid page source found for this url 'skip this link'
        #return False
        pass
    with open('exp' + str(page_no) + ".html", 'w', encoding='utf-8') as file:
        file.write(browser.page_source)
    y = bs(browser.page_source, 'html.parser')
    # print(page.text)

    # required divs
    divs = y.findAll('div', attrs={'class': 'g'})
    # print("--------divs-----------")
    # print(divs)

    current_links = []
    for div in divs:
        # print("------a----")
        for a in div.findAll('a'):
            # print(a)
            l = a.get('href')
            try:
                if l.startswith("https") and l not in links:
                    # l = re.sub(r"(^/url?q=)", "", l)
                    links.append(l)
                    current_links.append(l)
                elif l.startswith("http") and l not in links:
                    # l = re.sub(r"(^/url?q=)", "", l)
                    links.append(l)
                    current_links.append(l)
            except:
                pass
    # eliminating links which are not required
    # browser.close()
    return links, current_links



def get_scraper_for(key):
    '''
        Contains the xpath of the different sites where the text part belongs
    '''

    scrape_configs={"www.hindustantimes.com":"/html/body/div[1]/div[1]/div/div/div[1]/div/div[2]",
                    "www.thehindu.com":"//*[@id='content-body-14269002-29402419']"}
    
    return scrape_configs[key]




def scrap(link, sbo):
    '''
    Scraping the news links
    Removes:
    - head
    - header
    - footer
    - style
    - script
    If a existing scraper is found, good, else scrapes all <p> 
    '''
    data = {}
    key = link.split('/')[2]
    value = get_scraper_for(key)
    # proxy = generate_proxy(collector)
    # browser = init_selenium(proxy.host + ":" + proxy.port)
    retries = 3
    if not value:   # Generic Scrapping
        try:
            browser = sbo.connect(link, retries)
            page_source = browser.page_source
            y = bs(page_source)
            # Cleaning
            if y('head'):
                y.head.decompose()
            if y('header'):
                y.header.decompose()
            if y('footer'):
                y.footer.decompose()
            while y('style'):
                y.style.decompose()
            while y('script'):
                y.script.decompose()
            y = y.findAll('p')
            text = ""
            for p in y:
                text = text + "\n" + p.getText()
            # Furthur cleaning
            text = re.sub(r"(\n)|(\r)", " ", text)
            text = re.sub(
                r"(<script(\s|\S)*?<\/script>)|(<style(\s|\S)*?<\/style>)|(<!--(\s|\S)*?-->)|(<\/?(\s|\S)*?>)", '', text)
            data = {
                "textContent": text,
                "contentType": "web_scrapping",
                "metadata": {
                    "name": link
                }
            }
        except Exception as e:
            print("Web Scrapping Error: " + str(e))
            data = {}
        return data

    else:
        try:
            browser = sbo.connect(link, retries)
            text = browser.find_element_by_xpath(value).text
            data = {
                "textContent": text,
                "contentType": "web_scrapping"
            }
        except Exception as e:
            print("Web Scrapping Error: " + str(e))
            data = {}
        return data