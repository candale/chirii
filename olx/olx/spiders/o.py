# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request

from urllib.parse import urlparse, urlencode, urlunparse, unquote

from olx.items import OlxItem


class OSpider(scrapy.Spider):
    name = 'o'
    allowed_domains = ['olx.ro']
    # search queries here
    start_urls = [
        'https://www.olx.ro/imobiliare/case-de-inchiriat/cluj-napoca/?search[dist]=50&search[order]=created_at:desc',
        'https://www.olx.ro/cluj-napoca/q-casa-inchiriere/?search[dist]=30&search[order]=created_at:desc',
        'https://www.olx.ro/cluj-napoca/q-casa-chirie/?search[dist]=30&search[order]=created_at:desc',
        'https://www.olx.ro/cluj-napoca/q-casa-inchiriat/?search[dist]=30&search[order]=created_at:desc',
        'https://www.olx.ro/cluj-napoca/q-casa-inchiriez/?search[dist]=30&search[order]=created_at:desc',
        'https://www.olx.ro/cluj-napoca/q-vila-inchiriere/?search[dist]=30&search[order]=created_at:desc',
        'https://www.olx.ro/cluj-napoca/q-vila-inchiriat/?search[dist]=30&search[order]=created_at:desc',
        'https://www.olx.ro/cluj-napoca/q-vila-chirie/?search[dist]=30&search[order]=created_at:desc'
    ]
    handle_httpstatus_list = [403]

    def get_items_urls(self, response):
        return response.xpath("//td[contains(@class,'title-cell')]//a/@href").extract()

    def url_with_next_page(self, url):
        url_info = urlparse(unquote(url))
        query = dict(map(lambda x: x.split('='), url_info.query.split('&')))
        page = int(query.get('page', '1'))
        query['page'] = str(page + 1)
        url_info = url_info._replace(query=urlencode(query))

        return urlunparse(url_info)

    def parse(self, response):
        items_urls = self.get_items_urls(response)
        for url in items_urls:
            yield Request(url, callback=self.parse_item_page)

        all_pages = list(filter(
            None,
            map(
                lambda x: x.strip(),
                response.xpath('//div[contains(@class, "pager")]//span[contains(@class, "item")]//text()').extract()
            )
        ))

        cur_page = response.xpath('//div[contains(@class, "pager")]//span[contains(@class, "current")]//text()').extract()
        cur_page = list(filter(None, map(lambda x: x.strip(), cur_page)))
        if cur_page:
            cur_page = cur_page[0]

            if cur_page != all_pages[-1] and int(cur_page) <= 5:
                next_page_url = self.url_with_next_page(response.url)
                yield Request(next_page_url)

    def parse_item_page(self, response):
        url_info = urlparse(response.url)
        price = response.xpath("//strong[contains(@class, 'pricelabel')]//text()").extract_first()
        description = ' '.join(response.xpath("//div[@id='textContent']//text()").extract())

        return OlxItem(
            uid=url_info.path.split('-')[-1],
            title=response.xpath('//title/text()').extract_first(),
            price=price,
            url=response.url,
            description=description,
            has_backyard='curte' in description
        )
