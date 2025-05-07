import json
import logging
import time
from datetime import datetime

from webnovels.utils import NOVELS_DIR, create_new_novel, get_file_safe


class BaseScraper:
    def __init__(self, novel_url, novel_title):
        self.log = logging.getLogger(self.__class__.__name__)
        self.novel_url = novel_url

        # Setup novel directory
        self.novel_dir = NOVELS_DIR / get_file_safe(novel_title)
        if not self.novel_dir.exists():
            create_new_novel(novel_title)

        with open(self.novel_dir / 'metadata.json', 'r+') as metadata_file:
            metadata = json.load(metadata_file)
            metadata['url'] = novel_url
            json.dumps(metadata, indent=2)

    def close(self):
        pass

    def get(self, url):
        raise NotImplementedError

    def get_chapters(self):
        raise NotImplementedError

    def download_all_chapters(self, force=False):
        # if not force and list((self.novel_dir / 'raw_html').glob('*.html')):
        #     return
        # for file in (self.novel_dir / 'raw_html').glob('*'):
        #     file.unlink()

        chapter_links = self.get_chapters()
        chapter_data = []
        for i, chapter_link in enumerate(chapter_links, start=1):
            chapter_data.append({
                'name_index': i,
                'url': chapter_link,
                'chapter_title': '',  # Placeholder
            })

            fname = f'{i}.html'
            # with open(self.novel_dir / 'raw_html' / fname, 'w') as html_file:
            #     html_file.write(self.get(chapter_link))

            if bin(i).count('1') == 1:
                self.log.debug(f"Downloaded {i}/{len(chapter_links)} chapters")

        self.log.debug(f"Downloaded {i} chapters")

        chapter_data.sort(key=lambda info: info['name_index'])
        with open(self.novel_dir / 'metadata.json', 'r+') as metadata_file:
            metadata = json.load(metadata_file)
            metadata['chapter_info'] = chapter_data

            metadata['last_chapter_scrape_ts'] = time.time()
            metadata['last_chapter_scrape'] = datetime.now().isoformat()

            metadata_file.seek(0)
            json.dump(metadata, metadata_file, indent=2)

    def get_page_text(self):
        raise NotImplementedError

    def parse_chapter(self, chapter_html: str, fname: str) -> str:
        raise NotImplementedError

    def parse_all_chapters(self):
        with open(self.novel_dir / 'metadata.json', 'r') as metadata_file:
            metadata = json.load(metadata_file)

        for chapter_info in metadata['chapter_info']:
            i = chapter_info['name_index']

            with open(self.novel_dir / 'raw_html' / f'{i}.html', 'r') as html_file:
                response = html_file.read()
            chapter_info['chapter_title'] = self.parse_chapter(response, f'{i}.txt')

        with open(self.novel_dir / 'metadata.json', 'w') as metadata_file:
            json.dump(metadata, metadata_file, indent=2)
