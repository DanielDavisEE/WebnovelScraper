import logging

from webnovels.utils import NOVELS_DIR, create_new_novel


class BaseScraper:
    def __init__(self, novel_url, novel_name):
        self.log = logging.getLogger(self.__class__.__name__)
        self.novel_url = novel_url

        # Setup novel directory
        self.novel_dir = NOVELS_DIR / novel_name
        if not self.novel_dir.exists():
            create_new_novel(novel_name)

    def download_all_chapters(self, force=False):
        raise NotImplementedError

    def download_chapter(self):
        raise NotImplementedError

    def get_page_text(self):
        raise NotImplementedError
