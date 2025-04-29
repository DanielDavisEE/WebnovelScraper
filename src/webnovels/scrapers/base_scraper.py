class BaseScraper:
    def __init__(self, novel_url, novel_name):
        self.novel_url = novel_url
        self.novel_dir = novel_name

    def download_chapters(self, force=False):
        raise NotImplementedError

    def get_page_text(self):
        raise NotImplementedError
