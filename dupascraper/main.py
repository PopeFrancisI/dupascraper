import os
import re
from urllib.parse import urljoin
from urllib.request import urlretrieve

import bs4
import requests
import requests_html
import tqdm


session = requests_html.HTMLSession()  # FIXME


def soup_for_url(url: str):
    resp = requests.get(url)
    resp.raise_for_status()

    soup = bs4.BeautifulSoup(resp.text, 'html5lib')

    return soup


def rendered_soup_for_url(url: str):
    resp = session.get(url)
    resp.raise_for_status()

    resp.html: requests_html.HTML

    resp.html.render()

    soup = bs4.BeautifulSoup(resp.html.html, 'html5lib')

    return soup


def get_thread_urls(index_url: str):
    # soup = soup_for_url(index_url)
    soup = rendered_soup_for_url(index_url)

    threads = soup.select('#content #threads .thread > a')

    # thread_urls = []
    # for thread in threads:
    #     thread_urls.append(urljoin(index_url, thread.attrs['href']))

    thread_urls = [
        urljoin(index_url, thread.attrs['href'])
        for thread in threads
    ]

    return thread_urls


def extract_thread_files(thread_url: str):
    soup = soup_for_url(thread_url)

    posts = soup.select('.board .thread .postContainer')

    for post in posts:
        post: bs4.Tag

        if link_tag := post.select_one('a.fileThumb'):
            href = link_tag.attrs['href']

            file_url = urljoin(thread_url, href)

            yield file_url


def download_file(file_url: str):
    fname = re.search('/([\w\d_-]+\.[\w\d_-]+)$', file_url).group(1)
    urlretrieve(file_url, fname)


def download_thread(thread_url: str):
    _gen_it = extract_thread_files(thread_url)
    links = list(_gen_it)

    for file_url in tqdm.tqdm(links):
        download_file(file_url)


def main():
    index_url = 'https://boards.4chan.org/gif/catalog'

    root_dir = os.getcwd()

    for thread_url in tqdm.tqdm(get_thread_urls(index_url)):
        m = re.search('thread/(\d+)/?$', thread_url)
        thread_id = m.group(1)

        thread_dir = f'posts/{thread_id}'
        os.makedirs(thread_dir, exist_ok=True)

        os.chdir(thread_dir)
        try:
            download_thread(thread_url)
        finally:
            os.chdir(root_dir)

    # print("Hello, World!")
