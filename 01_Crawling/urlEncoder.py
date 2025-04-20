import urllib.parse

# Naver 검색어 퍼센트인코딩 후 url 반환
def URLEncoding(keyword):
    url = 'https://search.naver.com/search.naver?where=nexearch&sm=top_hty&fbm=0&ie=utf8&query='
    url.append(keyword)
    encoded_url = urllib.parse.quote(url, safe=':/&?=') 
    return encoded_url