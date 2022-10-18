import argparse
import asyncio
from collections import namedtuple

from aiohttp import ClientSession, ClientConnectionError

from bs4 import BeautifulSoup

ROOT_URL = 'https://news.ycombinator.com/'
SUCCESS_STATUS = 200

YPostDetail = namedtuple('YPostDetail', ['id', 'url', 'comment_urls'])


class URLFetcher():
    MAX_RECONNECT_TRIES = 5
    SUCCESS_STATUS = 200

    def __init__(self, session):
        self._session = session

    async def get(self, url):
        tries = 0
        try:
            async with self._session.get(url) as resp:
                if resp.status != self.SUCCESS_STATUS:
                    return None
                else:
                    return await resp.text()
        except (ClientConnectionError, asyncio.TimeoutError):
            await asyncio.sleep(0.5)
            tries += 1
        if tries >= self.MAX_RECONNECT_TRIES:
            return None


class YParser:
    def soup(self, html):
        return BeautifulSoup(html, 'html.parser')

    def get_post_ids(self, root_html):
        items = self.soup(root_html).findAll('tr', class_='athing')
        return [item['id'] for item in items]

    def get_post_detail(self, post_html):
        comm_urls = []
        item = self.soup(post_html).find('tr', class_='athing')
        id = item.get('id')
        links = self.soup(post_html).find_all('a')
        if links:
            post_url = links[0].get('href')
            for link in links[1:]:
                comm_urls.append(link.get('href'))
        ypost_detail = YPostDetail(id=id, url=post_url, comment_urls=comm_urls)
        return ypost_detail
    # def parse_url(self, url):
    #     if url==ROOT_URL:
    #         get_post_ids()
    #     else:
    #         if not url in processed_urls:


class YCrawler:

    def __init__(self, period):
        self.crawl_period = period


async def main():
    async with ClientSession() as session:
        tasks = []
        task = asyncio.create_task(URLFetcher(session).get(ROOT_URL))
        tasks.append(task)
        results = await asyncio.gather(*tasks)

        for result in results:
            print(result)


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-p', '--period', help='Crawling period', default=60, type=int)
    arg_parser.add_argument('-d', '--posts_dir', help='Loading dir', default='./posts', type=str)
    args = arg_parser.parse_args()

    asyncio.run(main())
