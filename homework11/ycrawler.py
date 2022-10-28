import argparse
import asyncio
import logging
import os
from collections import namedtuple

import aiohttp
import aiofiles

from bs4 import BeautifulSoup

ROOT_URL = 'https://news.ycombinator.com/'
CRAWLING_PERIOD = 100
CONCUR_LIMIT = 5

YPostDetail = namedtuple('YPostDetail', ['id', 'url', 'comment_urls'])


class URLFetcher:
    MAX_RECONNECT_TRIES = 7
    INTERVAL_RETRIES = 1
    SUCCESS_STATUS = 200

    def __init__(self, session):
        self._session = session

    async def get(self, url):
        tries = 0
        while True:
            try:
                async with self._session.get(url) as resp:
                    if resp.status != self.SUCCESS_STATUS:
                        logging.info(f'status ={resp.status}, url: {url}')
                        await asyncio.sleep(self.INTERVAL_RETRIES * 2 ** tries)
                        tries += 1
                        # return None
                    else:
                        return await resp.read()
            except Exception:
                await asyncio.sleep(self.INTERVAL_RETRIES * 2 ** tries)
                tries += 1
            if tries > self.MAX_RECONNECT_TRIES:
                logging.error(f'Unable to load url: {url}')
                return None

    async def get_with_semaphore(self, semaphore, url):
        async with semaphore:
            return await self.get(url)


class YParser:
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
        link = self.soup(post_html).find('span', class_="titleline").find('a')
        post_url = link.get('href')
        links = self.soup(post_html).select('div.comment a[rel=nofollow]')
        for link in links:
            comm_urls.append(link.get('href'))
        post_detail = YPostDetail(id=id, url=post_url, comment_urls=comm_urls)
        return post_detail


class YCrawler:

    def __init__(self, period, session):
        self.period = period
        self.queue = asyncio.Queue()
        self.processed_item_urls = []
        self.tasks = []
        self.path = args.posts_dir
        self.url_fetcher = URLFetcher(session)
        self.parser = YParser()
        self.semaphore = asyncio.Semaphore(value=CONCUR_LIMIT)

    async def run(self):
        task1 = asyncio.create_task(self.parse_urls_forever())
        self.tasks.append(task1)

        task2 = asyncio.create_task(self.process_urls_forever())
        self.tasks.append(task2)
        await asyncio.gather(*self.tasks)

    async def parse_urls_forever(self):
        while True:
            task = asyncio.create_task(
                self.parse_urls()
            )
            self.tasks.append(task)
            await asyncio.sleep(self.period)

    async def parse_urls(self):
        root_html = await self.url_fetcher.get(ROOT_URL)
        if not root_html:
            return
        post_ids = self.parser.get_post_ids(root_html)
        for id in post_ids:
            item_url = self.parser.get_post_item_url(id)
            if item_url in self.processed_item_urls:
                continue
            self.processed_item_urls.append(item_url)
            post_html = await self.url_fetcher.get(item_url)
            if not post_html:
                continue
            post_detail = self.parser.get_post_detail(post_html)
            id = post_detail.id
            post_url = post_detail.url
            comment_urls = post_detail.comment_urls
            logging.info(f'New post data with id: {id} put to queue')
            self.queue.put_nowait((id, post_url, comment_urls))

    async def process_urls_forever(self):
        while True:
            id, url, comm_urls = await self.queue.get()
            post_detail = YPostDetail(id=id, url=url, comment_urls=comm_urls)
            task = asyncio.create_task(
                self.load_urls_data(post_detail)
            )
            self.tasks.append(task)

    async def load_urls_data(self, post_detail):
        num = 0
        dest_dir = f'post_{post_detail.id}'
        dest_file = f'post.html'
        try:
            html = await self.url_fetcher.get_with_semaphore(self.semaphore, post_detail.url)
            if not html:
                return
            task = asyncio.create_task(
                self.load_html_to_path(dest_dir, dest_file, html)
            )
            self.tasks.append(task)
            logging.info(f'{post_detail.url} post_page saved to {dest_dir}')
        except Exception:
            logging.error(f'Unable to save page: {post_detail.url}')
        for url in post_detail.comment_urls:
            dest_file = f'comment_{num}.html'
            try:
                html = await self.url_fetcher.get(url)
                if html:
                    task = asyncio.create_task(
                        self.load_html_to_path(dest_dir, dest_file, html)
                    )
                    self.tasks.append(task)
                    logging.info(f'{url} comm_page saved to {dest_dir}')
                    num += 1
            except Exception:
                logging.error(f'Unable to save comm_page: {url}')
                return

    async def load_html_to_path(self, dest_dir, dest_file, html):
        if not os.path.exists(self.path):
            os.mkdir(self.path)
        path = os.path.join(self.path, dest_dir)
        if not os.path.exists(path):
            os.mkdir(path)
        dest_path = os.path.join(path, dest_file)
        async with aiofiles.open(dest_path, mode='wb') as f:
            await f.write(html)


async def main():
    connector = aiohttp.TCPConnector(ssl=False)
    async with aiohttp.ClientSession(
            connector=connector,
            timeout=aiohttp.ClientTimeout(total=10)
    ) as session:
        crawler = YCrawler(
            period=args.period,
            session=session
        )
        await crawler.run()


def logging_init(logging_file):
    # initialize script logging
    logging.basicConfig(filename=logging_file,
                        format='[%(asctime)s] %(levelname).1s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.INFO)


if __name__ == '__main__':
    logging_init(None)
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-p', '--period', help='Crawling period', default=CRAWLING_PERIOD, type=int)
    arg_parser.add_argument('-d', '--posts_dir', help='Loading dir', default='./posts', type=str)
    args = arg_parser.parse_args()
    asyncio.run(main())
