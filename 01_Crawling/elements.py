import re

# robots = {'domain':['path', 'path', ...]}
robots = dict()

# Remote Disconnected 방지 및 상대 사이트에서 bot 감지 위해서 내 User-agent
headers = {'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Whale/3.26.244.21 Safari/537.36'}

# Focused Crawling - 깊이 제한
limit = 3

# Focused Crawling - 도메인 제한
allow = [re.compile(re.escape('www.naver.com')),
         re.compile(r'naver.com$')]