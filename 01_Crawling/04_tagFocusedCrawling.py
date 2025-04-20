from requests import get
from requests.compat import urljoin, urlparse
from bs4 import BeautifulSoup
from time import sleep
import asyncio
import re
from elements import headers, limit, allow
from urlEncoder import URLEncoding
from fetch import canFetch, crawl_results


URLs = list()
Seens = list()

# HTML Tag 제한
async def crawl():
    # 앞으로 방문할 목록이 빌 때까지(더 이상 방문할 URL이 없을 때까지)
    while URLs:
        seed = URLs.pop(0)
        Seens.append(seed)

        if seed['depth'] > limit:
            continue

        if sum([m for m in
                map(lambda r: True if r.search(urlparse(seed['url']).netloc) else False,
                    allow)]) == 0:
            continue

        components = urlparse(seed['url'])

        if canFetch('://'.join(components[:2]), components.path) == False:
            print('Access Denied by Robot Parser')

        resp = get(seed['url'], headers=headers)

        if resp.status_code != 200:
            if resp.status_code == 500:
                URLs.append(seed['url'])
            else:
                print('No Response')
                continue

        print(seed['url'])
        if not re.search(r'text/html', resp.headers['content-type']):
            continue

        # HTML Tag 제한 => Whitelist: 어떤 것들이 반드시 있어야 함
        dom = BeautifulSoup(resp.text, 'html.parser')
        # tagname:ul, class:Nlnb_menu_list의 자손 중 li
        # li의 자식 중 tagname:a, class:Nitem_link, 속성 href가 있는 링크
        for link in dom.select('ul.Nlnb_menu_list li > a.Nitem_link[href]'):
            href = link.attrs['href'] if link.has_attr('href') else link.attrs['src']
            if not re.match(r'#|javascript', href):
                nurl = urljoin(seed['url'], href)
                if nurl not in [s['url'] for s in Seens] and \
                nurl not in [s['url'] for s in URLs]:
                    URLs.append({'url':nurl, 'depth':seed['depth']+1})
                    print({'url':nurl, 'depth':seed['depth']+1})

        # 해당 section에서의 뉴스 링크
        for link in dom.select('div.sa_text > a[href]'):
            href = link.attrs['href']
            if not re.match(r'#|javascript', href):
                nurl = urljoin(seed['url'], href)
                if nurl not in [s['url'] for s in Seens] and \
                nurl not in [s['url'] for s in URLs]:
                    URLs.append({'url':nurl, 'depth':seed['depth']+1})
                    print({'url':nurl, 'depth':seed['depth']+1})
        
        # 너무 많은 Traffic 발생시키지 않기 위해
        # sleep(1) # <= 난수

async def main():
    keyword = input("네이버 검색어 키워드를 입력해주세요: ")
    URLs.append(URLEncoding(keyword))
    await crawl()
    crawl_results(URLs, Seens)

asyncio.run(main())