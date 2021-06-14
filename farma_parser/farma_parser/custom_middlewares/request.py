import os

import scrapy.http
from w3lib.http import basic_auth_header


class ProxyMiddleware:
    def __init__(self, *args, **kwargs):
        super(ProxyMiddleware, self).__init__(*args, **kwargs)

        self._url = os.environ.get('PROXY_URL')
        self._username = os.environ.get('PROXY_USERNAME')
        self._password = os.environ.get('PROXY_PASSWORD')

        if not all([self._url, self._username, self._password]):
            raise NotImplemented

    def process_request(self, request: scrapy.http.Request, spider: scrapy.Spider):
        request.meta["proxy"] = self._url
        request.headers["Proxy-Authorization"] = basic_auth_header(self._username, self._password)
