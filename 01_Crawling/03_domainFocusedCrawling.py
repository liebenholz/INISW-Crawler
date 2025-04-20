from requests import request, get
from requests.compat import urljoin, urlparse, urlunparse
from bs4 import BeautifulSoup
from time import sleep
import asyncio
import re
from elements import headers, limit, allow
from urlEncoder import URLEncoding
from fetch import canFetch
from results import crawl_results

URLs = list()
Seens = list()
    
# 도메인 제한
async def crawl():
    # 앞으로 방문할 목록이 빌 때까지(더 이상 방문할 URL이 없을 때까지)
    while URLs:
        seed = URLs.pop(0)
        Seens.append(seed)

        # Focused Crawling
        # 깊이 제한(이것을 포함한다면 3번도 구현 완료)
        if seed['depth'] > limit:
            continue

        # 도메인 제한
        if sum([m for m in
                map(lambda r: True if r.search(urlparse(seed['url']).netloc) else False,
                    allow)]) == 0:
        # generator <= map(함수, iterator)
        # map(함수(iterator 객체):re.search() => Obj or None)
        # seed['URL'] = 'blog.naver.com'
        # => [re.search(www.naver.com, blog.naver.com) = False,
        #     re.search(naver.com$, blog.naver.com) = True]
        # sum([False, True]) = 1
        # if == 0이면 -> Whitelist(해당 도메인만 방문)
        #     > 0이면 -> Blacklist(해당 도메인 제외하고 나머지 방문)
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

        if not re.search(r'text/html', resp.headers['content-type']):
            continue

        dom = BeautifulSoup(resp.text, 'html.parser')
        for link in dom.select('a[href], iframe[src]'):
            href = link.attrs['href'] if link.has_attr('href') else link.attrs['src']
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