import json
from pathlib import Path

NOVELS_DIR = Path(__file__).parent / '.novels'


def get_file_safe(text):
    keepcharacters = (' ', '.', '_')
    return "".join(c for c in text if c.isalnum() or c in keepcharacters).rstrip()


def create_new_novel(title):
    novel_dir = NOVELS_DIR / get_file_safe(title)
    (novel_dir / '.resources').mkdir(parents=True)
    (novel_dir / '.resources' / 'dictionary_ext.txt').touch()
    (novel_dir / '.resources' / 'word_swaps.json').touch()

    (novel_dir / 'raw_html').mkdir(parents=True)
    (novel_dir / 'raw_chapters').mkdir(parents=True)
    (novel_dir / 'processed_chapters').mkdir(parents=True)
    (novel_dir / 'change_list.csv').touch()

    with open(novel_dir / 'metadata.json', 'w') as metadata:
        json.dump({'title': title}, metadata, indent=2)
