from urllib.parse import urlparse
from webnovels.scrapers.base_scraper import BaseScraper
from webnovels.scrapers.lightnovelworld_co import LightNovelWorldScraper


SITE_MAPPING = {
    "www.lightnovelworld.co": LightNovelWorldScraper
}


def get_scraper(novel_url, novel_name) -> BaseScraper:
    base_url = urlparse(novel_url).netloc
    if base_url not in SITE_MAPPING:
        raise ValueError(f"Invalid website: {base_url}")
    return SITE_MAPPING[base_url](novel_url, novel_name)


if __name__ == '__main__':
    novel_url = 'https://www.lightnovelworld.co/novel/the-perfect-run-24071713/'
    scraper = get_scraper(novel_url, 'The Perfect Run')
    scraper.download_all_chapters()
    scraper.parse_all_chapters()
