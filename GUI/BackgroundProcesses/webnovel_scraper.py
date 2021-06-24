import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

path = 'C:\Program Files\chromedriver_win32\chromedriver'
URL_BASE = 'https://wuxiaworld.site/novel/only-i-level-up/'#'https://www.readlightnovel.org/only-i-level-up'
TITLE = 'I Alone Level Up'

# prepare the option for the chrome driver
options = webdriver.ChromeOptions()
#options.add_argument('headless')

browser = webdriver.Chrome(path, 
                           chrome_options=options)
browser.implicitly_wait(10) # seconds
browser.get(URL_BASE)
WebDriverWait(browser, 30).until(EC.title_contains('Only'))

c = browser.page_source
soup = BeautifulSoup(c, features="html.parser")
with open(''.join([TITLE, '\Pages\index.txt']), 'w+', encoding='utf-8') as infile:
    infile.write(str(soup))

if 'readlightnovel' in URL_BASE:
    contents
    contents_class = "tab-content"
elif 'wuxiaworld.online' in URL_BASE:
    contents_class = "chapter-list"
elif 'wuxiaworld.site' in URL_BASE:
    contents_class = "page-content-listing single-page"
else:
    raise ValueError("Unknown website. Please add class of chapter contents.")
    
chapterlist = soup.find("div", class_=contents_class)

alist = chapterlist("a")

if 'wuxiaworld' in URL_BASE:
    alist.reverse()

chapter_dict = {}
chapter_template = {
    'title': None,
    'url': None,
    'soup_object': None,
    'text': None
    }

# Get list of chapter pages from index
for chapter in alist:
    link = chapter.get('href')
    tmp = chapter.string.strip(' \n\t').split(' ')
    i, chapter_name = int(tmp[1].strip(':')), ' '.join(tmp[2:])
    
    try:
        tmp = chapter_name.index('Only')
    except ValueError:
        pass
    else:
        chapter_name = chapter_name[:tmp]
    
    chapter_name = chapter_name.strip('1234567890/ ()-')
    
    if chapter_name == '':
        chapter_name = None
    #['title', 'url', 'soup_object', 'text']
    chapter_dict[i] = chapter_template.copy()
    chapter_dict[i]['title'] = chapter_name
    chapter_dict[i]['url'] = link
    print(i, chapter_name, link)

# Extract text from chapter pages
i = 1
for chapter in chapter_dict.values():
    print(f'Processing Chapter {i} / {len(chapter_dict)}...', end='\r')
    time.sleep(1)
    initial_time = time.time()
    try:
        browser.get(chapter['url'])
        #print(browser.title)
        WebDriverWait(browser, 30).until(EC.title_contains('Only'))
    except:
        #print(browser.title)
        browser.quit()
    finally:
        pass
        #print(int(time.time() - initial_time), 's')
    c = browser.page_source

    chapter['soup_object'] = BeautifulSoup(c, features="html.parser")
    invalid_symbols = "\\/?%*:|\"<>."
    
    fix_fn = lambda s: 'TBD' if chapter['title'] == None else s.translate({ord(j): None for j in invalid_symbols})
    with open((''.join([TITLE, '\Pages\{}. {}.txt'])).format(i, fix_fn(chapter['title'])), 
              'w+', encoding='utf-8') as infile:
        infile.write(str(chapter['soup_object']))
    
    i += 1

print(f'Web Scraping Completed, {i} Pages Copied.')

browser.quit()
