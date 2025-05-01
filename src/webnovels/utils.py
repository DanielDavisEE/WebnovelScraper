import json
from pathlib import Path

NOVELS_DIR = Path(__file__).parent / '.novels'


def get_file_safe(text):
    keepcharacters = (' ', '.', '_')
    return "".join(c for c in text if c.isalnum() or c in keepcharacters).rstrip()


def get_novel_dir(novel_title):
    novel_dir = NOVELS_DIR / get_file_safe(novel_title)
    if novel_dir.exists():
        return novel_dir
    else:
        raise RuntimeError('No directory found')


def create_new_novel(novel_title):
    novel_dir = NOVELS_DIR / get_file_safe(novel_title)
    (novel_dir / '.resources').mkdir(parents=True)
    (novel_dir / '.resources' / 'dictionary_ext.txt').touch()
    (novel_dir / '.resources' / 'word_swaps.json').touch()

    (novel_dir / 'raw_html').mkdir(parents=True)
    (novel_dir / 'raw_chapters').mkdir(parents=True)
    (novel_dir / 'processed_chapters').mkdir(parents=True)
    (novel_dir / 'change_list.csv').touch()

    with open(novel_dir / 'metadata.json', 'w') as metadata:
        json.dump({'title': novel_title}, metadata, indent=2)


def get_novel_titles():
    titles = []
    for novel_dir in NOVELS_DIR.glob('*'):
        if (novel_dir / 'metadata.json').exists():
            with open(novel_dir / 'metadata.json', 'r') as metadata:
                metadata = json.load(metadata)
            titles.append(metadata['title'])
    return titles


def get_novel_chapter_titles(novel_title):
    novel_dir = get_novel_dir(novel_title)

    if (novel_dir / 'raw_chapters' / 'index.json').exists():
        with open(novel_dir / 'raw_chapters' / 'index.json', 'r') as metadata:
            chapter_info = json.load(metadata)
        return [info[1] for info in sorted(chapter_info, key=lambda info: int(info[0].split('.')[0]))]


def get_chapter_text(novel_title, chapter_title):
    novel_dir = get_novel_dir(novel_title)

    if not (novel_dir / 'raw_chapters' / 'index.json').exists():
        raise RuntimeError

    with open(novel_dir / 'raw_chapters' / 'index.json', 'r') as metadata:
        chapter_info = json.load(metadata)
    fname = next(info[0] for info in chapter_info if info[1] == chapter_title)

    if not (novel_dir / 'raw_chapters' / fname).exists():
        raise RuntimeError

    with open(novel_dir / 'raw_chapters' / fname, 'r') as chapter_file:
        return chapter_file.read()