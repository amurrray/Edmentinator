import logging
import os
import requests
from random import randint
from lxml.html import fromstring
from pathlib import Path
from time import sleep

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import MoveTargetOutOfBoundsException, NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from slimit import ast
from slimit.parser import Parser as JavascriptParser
from slimit.visitors import nodevisitor
from fake_useragent import UserAgent

# setup logging
logging.basicConfig(level=logging.INFO, format=('%(asctime)s %(levelname)s %(name)s | %(message)s'))
logger = logging.getLogger('main')
logger.setLevel(logging.DEBUG)

# constants
if os.name == 'nt':
    CHROME_PATH = str(Path(__file__).resolve().parents[0]) + '/chromedriver.exe'
else:
    CHROME_PATH = str(Path(__file__).resolve().parents[0]) + '/chromedriver'
chrome_options = webdriver.ChromeOptions()
BASE_URL = "https://brainly.com/"
EXTENSION_PATH = str(Path(__file__).resolve().parents[0]) + '/buster2.crx'
DEBUG = True

def get_proxies():
    url = 'https://free-proxy-list.net/'
    response = requests.get(url)
    parser = fromstring(response.text)
    proxies = []
    for i in parser.xpath('//tbody/tr')[:10]:
        if i.xpath('.//td[7][contains(text(),"yes")]'):
            #Grabbing IP and corresponding PORT
            proxy = ":".join([i.xpath('.//td[1]/text()')[0],
                              i.xpath('.//td[2]/text()')[0]])
            proxies.append(proxy)
    return proxies

# proxies = get_proxies()
# PROXY = proxies[randint(0, (len(proxies) - 1))]
# chrome_options.add_argument('--proxy-server=%s' % PROXY)
# print(PROXY)

userAgent = UserAgent().random
logger.debug(userAgent)
# chrome_options.add_extension(EXTENSION_PATH)
chrome_options.add_argument(f'user-agent={userAgent}')
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)
chrome_options.add_argument("start-maximized")

driver = webdriver.Chrome(CHROME_PATH, options=chrome_options)
# driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
#     "source": """
#     Object.defineProperty(navigator, 'webdriver', {
#       get: () => undefined
#     })
#   """
# })
actions = ActionChains(driver)


# driver.get(BASE_URL)
# driver.get('https://www.expressvpn.com/what-is-my-ip')
# driver.get('https://brainly.com/app/ask?entry=hero&q=where+was+george+washington+born')
# driver.get('https://webcache.googleusercontent.com/search?q=cache:https://www.brainly.com')
# driver.get('https://brainly.com/app/ask?entry=hero&q=who+has+the+most+cheese')
# driver.get('http://useragentstring.com/')
driver.get('https://www.quora.com/Is-Brainly-the-same-as-Quora')
