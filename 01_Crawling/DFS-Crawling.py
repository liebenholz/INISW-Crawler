from requests import request, get
from requests.compat import urljoin, urlparse, urlunparse
from bs4 import BeautifulSoup
from time import sleep
import asyncio
import re
from elements import headers, limit
from urlEncoder import URLEncoding
from fetch import canFetch
from results import crawl_results

URLs = list()   # 앞으로 방문해야 할 URL 목록
Seens = list()  # 기존에 방문한 URL 목록
    
# 깊이 제한
async def crawl():
    # 앞으로 방문할 목록이 빌 때까지(더 이상 방문할 URL이 없을 때까지)
    while URLs:
        seed = URLs.pop(-1) # Stack, DFS
        Seens.append(seed)

        # 특정 깊이까지만 탐색
        if seed['depth'] > limit:
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

if __name__ == "__main__":
    asyncio.run(main())
     