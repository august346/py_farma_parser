import os
from typing import Generator, Iterable, Union
from urllib.parse import urljoin

import scrapy

from . import FarmaSpider


class GzSpider(FarmaSpider):
    name = 'gz'
    rate = 1

    start_urls = [os.environ['GZ_URL']]

    def parse(self, response: scrapy.http.Response, **kwargs) -> Iterable[Union[Generator, dict]]:
        yield from {
            None: self.parse_landing,
            "letter": self.parse_letter,
            "catalog": self.parse_catalog,
            "medicament": self.parse_medicament
        }[kwargs.get("page")](response)

    def parse_landing(self, response: scrapy.http.Response) -> Generator:
        return response.follow_all(
            # response.xpath('//a[has-class("c-alphabet-widget__sign")][not(@data-disabled)]')[48:],
            response.xpath('//a[has-class("c-alphabet-widget__sign")][not(@data-disabled)]'),
            callback=self.parse,
            cb_kwargs={"page": "letter"}
        )

    def parse_letter(self, response: scrapy.http.Response) -> Generator:
        return response.follow_all(
            response.xpath('//div[has-class("c-links-list")]').xpath('.//a'),
            callback=self.parse,
            cb_kwargs={"page": "catalog"}
        )

    def parse_catalog(self, response: scrapy.http.Response) -> Generator:
        return response.follow_all(
            (
                response
                .xpath('//div[has-class("c-product-tabs__target")]/following-sibling::div[1]')
                .xpath('.//a[has-class("c-prod-item__link")]')
            ),
            callback=self.parse,
            cb_kwargs={"page": "medicament"}
        )

    def parse_medicament(self, response: scrapy.http.Response) -> list[dict]:
        def groups():
            return (
                response
                .xpath('//div[@itemtype="http://schema.org/BreadcrumbList"]')
                .xpath('.//span[@itemprop="name"]/text()').getall()
            )[1:-1]

        def general():
            items = response.xpath('//div[@class="c-product__specs"]')

            if items:
                items = items[0]
            else:
                return {}

            return dict(
                zip(
                    items.xpath('.//*[has-class("c-product__label")]/text()').getall(),
                    items.xpath('.//*[has-class("c-product__description")]/text()').getall(),
                )
            )

        def specs():
            def row_pair(row):
                cells = [cell_text.strip() for cell_text in row.xpath('.//td/text()').getall()]
                return cells[0], '\n'.join(cells[1:])

            return dict(
                row_pair(row)
                for row in response.xpath('//div[has-class("c-product-tabs__target-tab")]//table//tr')
            )

        def images():
            items = response.xpath('//div[has-class("item", "js-product-preview__item")]')

            mains = items.xpath('.//@data-zoom-src').getall()
            thumbnails = items.xpath('.//img/@data-src').getall()

            return [
                dict(zip(["main", "thumbnail"], pair))
                for pair in zip(mains, thumbnails)
            ]

        def description():
            desc = response.xpath('//div[@itemprop="description"]')
            return dict(zip(
                desc.xpath('.//h3/text()').getall(),
                [
                    [s.strip() for s in d.xpath('.//text()').getall()]
                    for d in desc.xpath('.//div[has-class("b-text-block")]')
                ]
            ))

        def analogs():
            return [
                urljoin(self.start_urls[0], path)
                for path in response.xpath('//a[has-class("c-cross-sell__item-title")]/@href').getall()
            ]

        def price():
            try:
                return float(response.xpath('//meta[@itemprop="price"]/@content').get())
            except (TypeError, ValueError):
                return

        return [
            {
                "url": response.url,
                "title": response.xpath('//h1[has-class("b-page-title")][@itemprop="name"]/text()').get(),
                "groups": groups(),
                "general": general(),
                "specs": specs(),
                "images": images(),
                "description": description(),
                "analogs": analogs(),
                "price": price()
            }
        ]
