from functools import cached_property

import scrapy


class FarmaSpider(scrapy.Spider):
    @property
    def name(self) -> str:
        raise NotImplemented

    @property
    def rate(self) -> float:
        raise NotImplemented

    @property
    def download_delay(self) -> float:
        return 1 / self.rate

    def read_file(self, file_ext: str) -> str:
        with open(f'farma_parser/files/{self.name}.{file_ext}', 'r', encoding='utf-8') as file:
            return file.read()

    def parse(self, response, **kwargs):
        raise NotImplemented

    @staticmethod
    def _dict_to_list(data: dict) -> list[dict]:
        return [{'key': key, 'value': value} for key, value in data.items()]
