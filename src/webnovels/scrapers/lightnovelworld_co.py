from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from .base_scraper import BaseScraper

class LightNovelWorldScraper(BaseScraper):
    def __init__(self, novel_url, novel_name):
        super().__init__(novel_url, novel_name)

    def download_chapters(self):
        response = requests.get(urljoin(self.novel_url, 'chapters'))
        response.raise_for_status()

        index_soup = BeautifulSoup(response.text)
        chaps = index_soup.find("ul", class_="chapter-list").li
