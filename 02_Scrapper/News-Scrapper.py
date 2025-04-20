from requests import request, get
from requests.compat import urljoin, urlparse, urlunparse
from bs4 import BeautifulSoup
from time import sleep
import asyncio
import re
from elements import headers, limit, allow
from fetch import canFetch
from results import crawl_results

URLs = list()
Seens = list()
dom = BeautifulSoup()

async def scrap():
    while URLs:
        seed = URLs.pop(-1)
        Seens.append(seed)

        if seed['depth'] > limit:
            continue

        if sum([m for m in
                map(lambda r:True if r.search(urlparse(seed['url']).netloc) else False,
                    allow)]) == 0:
            continue

        components = urlparse(seed['url'])

        if canFetch('://'.join(components[:2]), components.path) == False:
            print('가져가면 안되요')

        resp = get(seed['url'], headers=headers)

        if resp.status_code != 200:
            if resp.status_code == 500:
                URLs.append(seed['url'])
            else:
                print('Response 없음')
                continue

        print(seed['url'])

        # 링크+본문 Scraping 영역
        if re.search(r'image/(?:jpeg|jpg|gif|png|bmp)', resp.headers['content-type']):
        # image
            name = re.sub(r'[?:;/$]', '', seed['url'])
            ext = re.search(r'image/(jpeg|jpg|gif|png|bmp)', resp.headers['content-type']).group(1)
            with open(name+'.'+ext, 'wb') as fp:
                fp.write(resp.content)

        elif re.search(r'text/html', resp.headers['content-type']):
        # text
            dom = BeautifulSoup(resp.text, 'html.parser')
            # HTML Tag 제한 =>

            # tagname:ul, class:Nlnb_menu_list 의 자손 중 li
            # li의 자식 중 tagname:a, class:Nitem_link, 속성 href가 있는 링크
            # section100, 101, ...
            for link in dom.select('ul.Nlnb_menu_list li > a.Nitem_link[href]'):
                href = link.attrs['href']
                if not re.match(r'#|javascript', href):
                    nurl = urljoin(seed['url'], href)
                    if nurl not in [s['url'] for s in Seens] and\
                    nurl not in [s['url'] for s in URLs]:
                        URLs.append({'url':nurl, 'depth':seed['depth']+1})
                        print({'url':nurl, 'depth':seed['depth']+1})

            # 해당 section에서의 뉴스링크
            for link in dom.select('div.sa_text > a[href]'):
                href = link.attrs['href']
                if not re.match(r'#|javascript', href):
                    nurl = urljoin(seed['url'], href)
                    if nurl not in [s['url'] for s in Seens] and\
                    nurl not in [s['url'] for s in URLs]:
                        URLs.append({'url':nurl, 'depth':seed['depth']+1})
                        print({'url':nurl, 'depth':seed['depth']+1})

            # Scraping
            if dom.select_one('#title_area, #dic_area'): # if None이면, 없다는 뜻(뉴스 본문이 아님)
                # 본문 내 이미지 링크
                for link in dom.select('#dic_area img[data-src]'):
                    href = link.attrs['data-src']
                    if not re.match(r'#|javascript', href):
                        nurl = urljoin(seed['url'], href)
                        if nurl not in [s['url'] for s in Seens] and\
                        nurl not in [s['url'] for s in URLs]:
                            URLs.append({'url':nurl, 'depth':seed['depth']+1})
                            print({'url':nurl, 'depth':seed['depth']+1})

                title = dom.select_one('#title_area')
                content = dom.select_one('#dic_area')
                g = re.search(r'(\d{3})/(\d{5,})$', seed['url'])
                with open(g.group(1)+'-'+g.group(2)+'.txt', 'w', encoding='utf8') as fp:
                    fp.write(title.text+'\n\n')
                    fp.write(content.text)

async def main():
    URLs.append({
        'url':'https://news.naver.com/',
        'depth':1
    })    
    await scrap()
    crawl_results()

if __name__ == "__main__":
    asyncio.run(main())