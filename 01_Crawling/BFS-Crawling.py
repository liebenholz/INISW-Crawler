from requests import request, get
from requests.compat import urljoin, urlparse, urlunparse
from bs4 import BeautifulSoup
from time import sleep
import asyncio
import re
from elements import headers
from urlEncoder import URLEncoding
from fetch import canFetch
from results import crawl_results

URLs = list()   # 앞으로 방문해야 할 URL 목록
Seens = list()  # 기존에 방문한 URL 목록

    
async def crawl():
    # 앞으로 방문할 목록이 빌 때까지(더 이상 방문할 URL이 없을 때까지)
    while URLs:
        # BFS(관련성)를 위한 Queue:0, DFS(세부적)를 구현한다면 Stack:-1
        seed = URLs.pop(0) # pop()하면 순차적으로 꺼내기
        Seens.append(seed) # seed는 실제 방문을 하던, 오류나 중복 등으로 방문하지 않던, 방문한 목록에 추가

        components = urlparse(seed) # robotsParser의 parameter를 위해

        # (scheme, netloc, path, params, qs, fragment)
        # canfetch('scheme://netloc', 'path')
        if canFetch('://'.join(components[:2]), components.path) == False:
            print('Access Denied by Robot Parser')

        # Request - Response
        resp = get(seed, headers=headers)

        if resp.status_code != 200:
            # 400 or 500 error
            # 500번대는 ServerError, 나중에 다시 시도
            if resp.status_code == 500:
                URLs.append(seed)
            else:
            # 400번대는 ClientError, 방문하지 않도록
                print('No Response')
                continue # 밑에 실행 안하고, 다음 while => URLs.pop() -> 다음 주소로 이동

        # text/*, application/*, image/*, ...
        # Hyperlink in TEXT/HTML
        # HTML.Response.Headers에 TEXT/HTML인지 확인
        if not re.search(r'text/html', resp.headers['content-type']):
            continue

        # HTML -> DOM
        dom = BeautifulSoup(resp.text, 'html.parser')
        # A(href 속성이 있는), IFRAME(src 속성이 있는)
        for link in dom.select('a[href], iframe[src]'):
            # href = 만약 href 속성이 있으면 href, 아니면 src
            href = link.attrs['href'] if link.has_attr('href') else link.attrs['src']
            if not re.match(r'#|javascript', href):
                # http://다른주소
                # #top
                # javascript:func()
                # mailto:
                # tel:
                nurl = urljoin(seed, href)

                # URL 정규화, /다른페이지 => http://netloc/다른페이지
                if nurl not in Seens and \
                nurl not in URLs: # 한번이라도 방문한적이 없으면(Seens와 URLs 모두)
                    # 앞으로 방문할 URL
                    URLs.append(nurl)
                    print(nurl)

        # 너무 많은 Traffic 발생시키지 않기 위해
        # sleep(1) # <= 난수

async def main():
    keyword = input("네이버 검색어 키워드를 입력해주세요: ")
    URLs.append(URLEncoding(keyword))
    await crawl()
    crawl_results(URLs, Seens)

if __name__ == "__main__":
    asyncio.run(main())
     