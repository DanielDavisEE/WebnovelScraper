import json
from pathlib import Path

NOVELS_DIR = Path(__file__).parent / '.novels'
WHITESPACE = set(' \n\t')

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
    (novel_dir / 'change_lists').mkdir(parents=True)

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


def get_chapter_info(novel_title):
    novel_dir = get_novel_dir(novel_title)

    if not (novel_dir / 'metadata.json').exists():
        raise RuntimeError

    with open(novel_dir / 'metadata.json', 'r') as metadata_file:
        metadata = json.load(metadata_file)

    if 'chapter_info' not in metadata:
        raise RuntimeError

    return metadata['chapter_info']


def get_novel_chapter_titles(novel_title):
    return [info['chapter_title'] for info in get_chapter_info(novel_title)]


def get_chapter_index(novel_title, chapter_title):
    index = next((info['name_index'] for info in get_chapter_info(novel_title) if info['chapter_title'] == chapter_title), None)
    if index is None:
        raise RuntimeError(f"Could not find chapter '{chapter_title}' in novel '{novel_title}'")
    return index


def to_tk_index(text: str, index: int):
    lines = text[:index].split('\n')
    line_no = len(lines)
    col_no = len(lines[-1])
    return f"{line_no}.{col_no}"


def to_str_index(text: str, tk_index: str):
    line_str, col_str = tk_index.split('.')
    line = int(line_str)
    col = int(col_str)

    lines = text.split('\n')
    if line > len(lines):
        raise IndexError("Line number out of range.")

    # Sum lengths of lines before the target one (including newline chars)
    char_index = sum(len(ln) + 1 for ln in lines[:line - 1]) + col
    return char_index
