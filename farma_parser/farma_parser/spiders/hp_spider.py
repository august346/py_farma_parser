import os
from typing import Generator, Iterable, Union

import scrapy


class HpSpider(scrapy.Spider):
    name = 'hp'
    rate = 1

    start_urls = [os.environ['HP_URL']]

    @property
    def download_delay(self) -> float:
        return 1 / self.rate

    def parse(self, response: scrapy.http.Response, **kwargs) -> Iterable[Union[Generator, dict]]:
        yield from {
            None: self.parse_landing,
            "letter": self.parse_letter,
            "mnn": self.parse_mnn,
            "medicament": self.parse_medicament
        }[kwargs.get("page")](response)

    def parse_landing(self, response: scrapy.http.Response) -> Generator:
        for href in response.css('li.main-alphabet__nav-item a::attr(href)').getall():
            yield response.follow(href, callback=self.parse, cb_kwargs={"page": "letter"}, flags=[href])

    def parse_letter(self, response: scrapy.http.Response) -> Generator:
        return response.follow_all(
            response.css('.main-alphabet__list a'),
            callback=self.parse,
            cb_kwargs={"page": "mnn"}
        )

    def parse_mnn(self, response: scrapy.http.Response) -> Generator:
        yield from response.follow_all(
            response.css('.card-list .product-card .product-card__title a'),
            callback=self.parse,
            cb_kwargs={"page": "medicament"}
        )

        page_number = response.css('.pagination__item_active::text').get()

        if page_number and page_number.strip() == '1':
            yield from response.follow_all(
                response.css('a.pagination__item'),
                callback=self.parse,
                cb_kwargs={"page": "mnn"}
            )

    def parse_medicament(self, response: scrapy.http.Response) -> list[dict]:
        def stripped_not_empty(texts: list[str]) -> list[str]:
            return [
                stripped
                for x in texts
                if (stripped := (x or '').strip())
            ]

        def groups():
            return (
                response
                .xpath('//div[@itemtype="http://schema.org/BreadcrumbList"]')
                .xpath('.//a[@itemprop="name"]/@title').getall()
            )[2:]

        def general():
            results = {}

            for tr in response.xpath('//table[has-class("product-detail__spec")]/tr'):
                key = None
                for i, td in enumerate(tr.xpath('.//td')):
                    if i == 0:
                        key = td.css('::text').get()
                    else:
                        results[key] = stripped_not_empty(td.css('::text').getall())

            return results

        def description():
            parts = (
                response
                .xpath('//div[@class="product-detail-description"][@itemprop="description"]')
                .xpath('.//div[has-class("product-detail-description-content__item")]')
            )[:-1]

            return {
                p.xpath('.//div[has-class("product-detail-description-content__item-h")]/h3/text()').get():
                stripped_not_empty(
                    p.xpath('.//div[has-class("product-detail-description-content__item-content")]')
                    .css('::text').getall()
                )
                for p in parts[:-1]
            }

        def price():
            try:
                return float(response.xpath('//meta[@itemprop="price"]/@content').get())
            except (TypeError, ValueError):
                return

        return [
            {
                "url": response.url,
                "title": (response.css('h1.product-detail__title::text').get() or '').strip(),
                "groups": groups(),
                "general": general(),
                "images": response.xpath('//div[@data-fancybox="gallery"]/@href').getall(),
                "description": description(),
                "price": price()
            }
        ]
