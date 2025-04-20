from requests import get
from requests.compat import urlparse
import re
from elements import robots, headers

def canFetch(host, path):
    # 반드시 https로 시작해야지만 정상적인 URL, 이를 위한 검사
    if not re.search('^https?', host):
        return 'Scheme 오류'

    url = host+'/' if host[-1] != '/' else host
    # URL 가장 마지막에 /robots.txt를 붙이기 위해 필요
    # www.naver.comrobots.txt => www.naver.com/robots.txt
    url += 'robots.txt'

    # urlparse(https://www.naver.com).netloc => k=www.naver.com
    k = urlparse(url).netloc
    # k not in robots{'www.naver.com':['path', 'path', ...]}
    # k(www.naver.com)가 dict에 없을 경우,
    if k not in robots.keys():
        resp = get(url, headers=headers)

        # netloc/robots.txt에 접근X (없어서, 서버가 응답X)
        if resp.status_code != 200:
            print(resp.status_code)
            return True

        # if k not in robots.keys():
        robots[k] = re.findall('^disallow:\s*(.+)$', resp.text, re.IGNORECASE|re.MULTILINE)

    # dict[k] = 'path', 'path', ...]
    # path in 'path', 'path', ...]
    if path in robots[k]:
        return False
    # 명시적으로 거부하지 않았기에, opt-out(blacklist)에 의해서 True
    else:
        # path.split('/') # 나중에 완성
        return True