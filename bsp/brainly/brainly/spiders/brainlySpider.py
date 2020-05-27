# -*- coding: utf-8 -*-
import scrapy
import logging
from scrapy.linkextractors import LinkExtractor
from scrapy_splash import SplashRequest

class brainlySpider(scrapy.Spider):
    name = 'brainlySpider'
    allowed_domains = ['google.com']
    start_urls = ['https://google.com/']

    def __init__(self, *args, **kwargs):
        logger = logging.getLogger('brainlySpider')
        logging.basicConfig(level=logging.INFO, format=('%(asctime)s %(levelname)s %(name)s | %(message)s'))
        super().__init__(name=name, **kwargs)

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, self.parse,
                                endpoint='render.html',
                                args={'wait': 0.5},
                                )

    def parse(self, response):
        self.logger.info(f'parsing {response.url}')
        # response
        pass

if __name__ == "__main__":
    pass
