# -*- coding: utf-8 -*-
import scrapy

from scrapy.linkextractors import LinkExtractor
from scrapy_splash import SplashRequest

class BrainlyspiderSpider(scrapy.Spider):
    name = 'brainlySpider'
    allowed_domains = ['google.com']
    start_urls = ['http://google.com/']

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, self.parse,
                                endpoint='render.html',
                                args={'wait': 0.5},
                                )

    def parse(self, response):
        pass
