import json
import time
from pathlib import Path
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

from .base_scraper import BaseScraper

import logging


class LightNovelWorldScraper(BaseScraper):
    def __init__(self, novel_url, novel_name):
        super().__init__(novel_url, novel_name)

        # Set up Selenium WebDriver (adjust path as needed)
        driver_path = Path(r"D:\Daniel Davis\Documents\Webdrivers\chromedriver-win64\chromedriver.exe").resolve()
        service = Service(driver_path)
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")  # Optional: Run in headless mode

        self.driver = webdriver.Chrome(service=service, options=options)

    def close(self):
        self.driver.quit()

    def get(self, url):
        if self.novel_url not in url:
            url = urljoin(self.novel_url, url)
        self.driver.get(url)

        time.sleep(2)
        # TODO
        # wait = WebDriverWait(self.driver, 10)  # Wait up to 10 seconds
        # wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'chapter-list')))

        return self.driver.page_source

    def get_chapters(self):
        response = self.get('chapters')
        index_soup = BeautifulSoup(response, 'html.parser')

        tabs = index_soup.find('ul', class_='pagination')
        tab_numbers = [span.text for span in tabs.find_all('li') if span.text.isalnum()]

        chapters = []
        for page_num in tab_numbers:
            response = self.get(f'chapters?page={page_num}')
            index_soup = BeautifulSoup(response, 'html.parser')
            ul_soup = index_soup.find('ul', class_='chapter-list')
            if ul_soup:
                chapters += [chapter_link['href'] for chapter_link in ul_soup.find_all('a', href=True)]

        if not chapters:
            raise RuntimeError("No chapter-list <ul> found.")
        return chapters

    def download_all_chapters(self, force=False):
        if not force and list((self.novel_dir / 'raw_pages').glob('*.html')):
            return
        for file in (self.novel_dir / 'raw_pages').glob('*'):
            file.unlink()

        chapter_links = self.get_chapters()
        chapter_data = []
        for i, chapter_link in enumerate(chapter_links, start=1):
            fname = f'{i}.html'
            chapter_data.append((fname, chapter_link))

            with open(self.novel_dir / 'raw_pages' / fname, 'w') as html_file:
                html_file.write(self.get(chapter_link))

            if bin(i).count('1') == 1:
                self.log.debug(f"Downloaded {i} chapters")

        self.log.debug(f"Downloaded {i} chapters")

        chapter_data.sort()
        with open(self.novel_dir / 'raw_pages' / 'index.json', 'w') as index_file:
            json.dump(chapter_data, index_file)

    def parse_chapter(self, chapter_html, fname):
        index_soup = BeautifulSoup(chapter_html, 'html.parser')

        chapter_title = index_soup.find('span', class_='chapter-title').text
        page_text = '\n'.join([str(p) for p in index_soup.find('div', id='chapter-container').find_all('p')])

        with open(self.novel_dir / 'chapters' / fname, 'w') as chapter_file:
            chapter_file.write(page_text)

        return fname, chapter_title

    def parse_all_chapters(self):
        with open(self.novel_dir / 'raw_pages' / 'index.json', 'r') as index_file:
            chapter_files = json.load(index_file)

        chapter_data = []
        for chapter_file, _url in chapter_files:
            with open(self.novel_dir / 'raw_pages' / chapter_file, 'r') as html_file:
                response = html_file.read()
            chapter_data.append(self.parse_chapter(response, chapter_file.replace('html', 'txt')))

        chapter_data.sort()
        with open(self.novel_dir / 'chapters' / 'index.json', 'w') as index_file:
            json.dump(chapter_data, index_file)

