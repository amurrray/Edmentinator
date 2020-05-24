# -*- coding: utf-8 -*-
import scrapy

from scrapy.linkextractors import LinkExtractor
from scrapy_splash import SplashRequest

class BrainlyspiderSpider(scrapy.Spider):
    name = 'brainlySpider'
    allowed_domains = ['brainly.com']
    start_urls = ['http://brainly.com/']

    def parse(self, response):
        pass
