import json
import logging
import time
from datetime import datetime

from webnovels.utils import NOVELS_DIR, create_new_novel


class BaseScraper:
    def __init__(self, novel_url, novel_name):
        self.log = logging.getLogger(self.__class__.__name__)
        self.novel_url = novel_url

        # Setup novel directory
        self.novel_dir = NOVELS_DIR / novel_name
        if not self.novel_dir.exists():
            create_new_novel(novel_name)

    def close(self):
        pass

    def get(self, url):
        raise NotImplementedError

    def get_chapters(self):
        raise NotImplementedError

    def download_all_chapters(self, force=False):
        if not force and list((self.novel_dir / 'raw_html').glob('*.html')):
            return
        for file in (self.novel_dir / 'raw_html').glob('*'):
            file.unlink()

        chapter_links = self.get_chapters()
        chapter_data = []
        for i, chapter_link in enumerate(chapter_links, start=1):
            fname = f'{i}.html'
            chapter_data.append((fname, chapter_link))

            with open(self.novel_dir / 'raw_html' / fname, 'w') as html_file:
                html_file.write(self.get(chapter_link))

            if bin(i).count('1') == 1:
                self.log.debug(f"Downloaded {i} chapters")

        self.log.debug(f"Downloaded {i} chapters")

        chapter_data.sort()
        with open(self.novel_dir / 'raw_html' / 'index.json', 'w') as index_file:
            json.dump(chapter_data, index_file, indent=2)

        with open(self.novel_dir / 'metadata.json') as metadata_file:
            metadata = json.load(metadata_file)
            metadata['last_chapter_scrape_ts'] = time.time()
            metadata['last_chapter_scrape'] = datetime.now().isoformat()
            json.dump(metadata, metadata_file, indent=2)

    def get_page_text(self):
        raise NotImplementedError

    def parse_chapter(self, chapter_html, fname) -> [str, str]:
        raise NotImplementedError

    def parse_all_chapters(self):
        with open(self.novel_dir / 'raw_html' / 'index.json', 'r') as index_file:
            chapter_files = json.load(index_file)

        chapter_data = []
        for chapter_file, _url in chapter_files:
            with open(self.novel_dir / 'raw_html' / chapter_file, 'r') as html_file:
                response = html_file.read()
            chapter_data.append(self.parse_chapter(response, chapter_file.replace('html', 'txt')))

            (self.novel_dir / 'change_lists' / chapter_file.replace('html', 'csv')).touch()

        chapter_data.sort()
        with open(self.novel_dir / 'raw_chapters' / 'index.json', 'w') as index_file:
            json.dump(chapter_data, index_file, indent=2)
