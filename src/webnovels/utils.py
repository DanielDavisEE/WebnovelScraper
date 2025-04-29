from pathlib import Path

NOVELS_DIR = Path(__file__).parent / '.novels'


def create_new_novel(title):
    keepcharacters = (' ', '.', '_')
    safe_name = "".join(c for c in title if c.isalnum() or c in keepcharacters).rstrip()

    novel_dir = NOVELS_DIR / safe_name
    (novel_dir / 'raw_pages').mkdir(parents=True)
    (novel_dir / 'dictionary.txt').touch()
    (novel_dir / 'change_list.csv').touch()
    (novel_dir / 'chapter_list.csv').touch()
