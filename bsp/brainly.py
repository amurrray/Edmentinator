import logging
import os
import requests
import pickle
from random import randint
from lxml.html import fromstring
from pathlib import Path
from time import sleep

from bs4 import BeautifulSoup
from fake_useragent import UserAgent

# setup logging
logging.basicConfig(level=logging.INFO, format=('%(asctime)s %(levelname)s %(name)s | %(message)s'))
logger = logging.getLogger('main')
logger.setLevel(logging.DEBUG)

# constants
BASE_URL = "https://brainly.com/"
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

proxies = get_proxies()
PROXY = proxies[randint(0, (len(proxies) - 1))]
logger.debug(PROXY)

userAgent = UserAgent().random
logger.debug(userAgent)

datadomeKey = input('insert datadome key: ')

def query(query):
    query.replace(' ', '+')

answers = pickle.load(open('answers.pkl', 'rb'))
s = requests.session()
my_cookie = requests.cookies.create_cookie('datadome', datadomeKey)

s.cookies.set_cookie(my_cookie)
r = s.get('https://brainly.com/question/3021648')

print(r.text)

# query('where was george washington born')
# use requests tard, just send it same way as browser?
pickle.dump(answers, open('answers.pkl', 'wb'))
