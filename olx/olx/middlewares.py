# -*- coding: utf-8 -*-
import os
from urllib.parse import urlparse

from scrapy import exceptions


class IgnoreExistingMiddleware(object):

    def __init__(self, uids_so_far=None):
        self.uids_so_far = set(uids_so_far)

    @classmethod
    def from_crawler(cls, crawler):
        if os.path.exists('uids.txt'):
            with open('uids.txt', 'r') as f:
                uids_so_far = list(filter(None, map(lambda x: x.strip().lower(), f)))
        else:
            uids_so_far = []

        return cls(
            uids_so_far=uids_so_far
        )

    def should_be_scraped(self, request):
        url_info = urlparse(request.url)
        uid = url_info.path.split('-')[-1].lower()

        return uid not in self.uids_so_far

    def process_request(self, request, spider):
        if self.should_be_scraped(request) is False:
            print('SKIP ITEM')
            raise exceptions.IgnoreRequest
