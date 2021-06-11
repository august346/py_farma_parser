import json
import os
from functools import cached_property
from typing import Callable, Optional

import jq
import scrapy

URL = os.environ['OZ_URL']


class QuotesSpider(scrapy.Spider):
    name = 'oz'
    stop = False
    rate = 0.5

    @property
    def download_delay(self) -> float:
        return 1 / self.rate

    @cached_property
    def graphql_query(self) -> str:
        return self.read_file('graphql')

    @cached_property
    def jq_query(self) -> str:
        return self.read_file('jq')

    def read_file(self, file_ext: str) -> str:
        with open(f'farma_parser/files/{self.name}.{file_ext}', 'r', encoding='utf-8') as file:
            return file.read()

    def start_requests(self):
        yield self.get_request(0)

    def get_request(self, page: int, callback: Optional[Callable] = None) -> scrapy.http.JsonRequest:
        return scrapy.http.JsonRequest(
            url=URL,
            method='POST',
            data={
                'query': self.graphql_query,
                'variables': {'page': page, 'size': 20}
            },
            callback=callback
        )

    def parse(self, response: scrapy.http.TextResponse, **kwargs):
        items = jq.compile(self.jq_query).input(response.json()).first()

        yield from items

        if len(items) > 0:
            yield self.get_next_request(response)

    def get_next_request(self, response: scrapy.http.TextResponse) -> scrapy.http.JsonRequest:
        return self.get_request(json.loads(response.request.body)['variables']['page'] + 1, self.parse)
