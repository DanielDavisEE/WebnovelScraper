import abc

import requests
from bs4 import BeautifulSoup


class BaseScraper(abc.ABCMeta):
    def __init__(self):
def get_chapters(index_page):
    response = requests.get(index_page)
    response.raise_for_status()

    index_soup = BeautifulSoup(response.text)