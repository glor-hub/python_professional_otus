import argparse
import asyncio
import os
from collections import namedtuple

from aiohttp import ClientSession, ClientConnectionError
from aiofile import async_open

from bs4 import BeautifulSoup

ROOT_URL = 'https://news.ycombinator.com/'
CRAWLING_PERIOD = 60

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


class YParser():
    def soup(self, html):
        return BeautifulSoup(html, 'html.parser')

    def get_post_ids(self, root_html):
        items = self.soup(root_html).findAll('tr', class_='athing')
        return [item['id'] for item in items]

    def get_post_item_url(self, post_id):
        return ROOT_URL + f'/item?id={post_id}'

    def get_post_detail(self, post_html):
        comm_urls = []
        item = self.soup(post_html).find('tr', class_='athing')
        id = item.get('id')
        links = self.soup(post_html).find_all('a')
        if links:
            post_url = links[0].get('href')
            for link in links[1:]:
                comm_urls.append(link.get('href'))
        post_detail = YPostDetail(id=id, url=post_url, comment_urls=comm_urls)
        return post_detail


class YCrawler:

    def __init__(self, period, session):
        self.period = period
        self.queue = asyncio.Queue()
        self.processed_item_urls = []
        self.tasks = []
        self.path = args.post_dir
        self.url_fetcher = URLFetcher(session)
        self.parser = YParser()

    async def run(self):
        task = asyncio.create_task(
            self.process_urls_forever()
        )
        self.tasks.append(task)
        await asyncio.gather(*self.tasks)

    def parse(self, html):

    async def process_urls_forever(self):
        while True:
            self.process_urls()
            await asyncio.sleep(self.period)

    async def process_urls(self):
        root_html = await self.url_fetcher.get(ROOT_URL)
        post_ids = self.parser.get_post_ids(root_html)
        for id in post_ids:
            item_url = self.parser.get_post_item_url(id)
            if not item_url in self.processed_item_urls:
                self.processed_item_urls.append(item_url)
                post_html = await self.url_fetcher.get(item_url)
                post_detail = get_post_detail(post_html)
                id = post_detail.id
                post_url = post_detail.url
                comment_urls = post_detail.comment_urls
                await self.queue.put((id, post_url, comment_urls))

    async def load_post_data(self):
        num = 0
        id, url, comm_urls = await self.queue.get()
        dest_dir = f'post_{id}'
        dest_file = f'post.html'
        await html = self.url_fetcher.get(url)
        await self.load_html_to_path(dest_dir, dest_file, html)
        for url in comm_urls:
            dest_file = f'comment_{num}.html'
            await html = self.url_fetcher.get(url)
            await self.load_html_to_path(dest_dir, dest_file, html)
            num += 1

    async def load_html_to_path(self, dest_dir, dest_file, html):
        if not os.path.exists(self.path):
            os.mkdir(self.path)
            dest_path = os.path.join(self.path, dest_dir, dest_file)
            async with async_open(dest_path, mode='wb') as f:
                await f.write(html)


async def main():
    async with ClientSession() as session:
        crawler = YCrawler(
            period=CRAWLING_PERIOD,
            session=session
        )
        await crawler.run()


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-p', '--period', help='Crawling period', default=60, type=int)
    arg_parser.add_argument('-d', '--posts_dir', help='Loading dir', default='./posts', type=str)
    args = arg_parser.parse_args()

    asyncio.run(main())
