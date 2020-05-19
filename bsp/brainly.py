import logging
import os
import requests
from requests_html import HTMLSession
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

def query(query):
    # generate query url so that the user can get datadome key
    query = query.replace(' ', '+')
    queryUrl = BASE_URL + 'app/ask?entry=top&q=' + query
    print(queryUrl)
    answers = pickle.load(open('answers.pkl', 'rb'))

    # make the request look like it came from a user browser
    s = requests.session()
    s = HTMLSession()
    datadomeKey = input('insert datadome key: ')
    my_cookie = requests.cookies.create_cookie('datadome', datadomeKey)
    s.headers.update({'User-Agent': userAgent})
    s.cookies.set_cookie(my_cookie)

    r = s.get(queryUrl)
    # THIS DOESNT FKIN WORK CUZ BRAINLY USES JS TO GENERATE THE SEARCH PAGE

    soup = BeautifulSoup(r.text, 'lxml')

    questions = soup.find_all('a', href=True)
    file = open('resp.html', 'w')
    file.write(r.text)
    file.close()
    answers = soup.find_all('a', class_='sg-text sg-text--small sg-text--link sg-text--bold sg-text--blue-dark')

    for answer in answers:
        print(answer)

    pickle.dump(answers, open('answers.pkl', 'wb'))

if __name__ == "__main__":
    query('where was george washington born')
