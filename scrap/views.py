"""
datetime: 시간파악을 위함
logging: 로깅
re: 정규표현식 검색을 위함
requests: http 요청을 하기 위함
BeautifulSoup: 웹 스크래핑을 위함
"""
import datetime
import logging
import re
from django.shortcuts import render
import requests
from bs4 import BeautifulSoup
import redis

from .forms import UrlForm
from .models import ScrappedUrl

# Create your views here.

LOGGER = logging.getLogger(__name__)

redis_client1 = redis.StrictRedis(host = 'localhost' , port = 6379)
redis_client2 = redis.StrictRedis(host = 'localhost' , port = 6380)
redis_client3 = redis.StrictRedis(host = 'localhost' , port = 6381)


def main_view(request):
    """
    애플리케이션의 메인 뷰.

    POST:param request: 뷰단의 request
    POST:return: 스크래핑된 url 데이터를 포함한 main_view.html이 렌더링된 것을 리턴

    GET:param request: request
    GET:return: 새로고침된 main_view.html이 렌더링된 것을 리턴
    """
    dict_return = {}
    form = UrlForm()
#    redis_client1.set('sample', 'Hello World')    
    print(redis_client1)
    print(redis_client2)
    print(redis_client3)

    hello = redis_client1.get('sample') 
    if hello is not None:
        hello = hello.decode()
    else:
        hello = "None"
    print('test:::' + hello)
    
    hello = redis_client2.get('sample') 

    if request.method == 'POST':  # 웹 스크래핑 버튼을 눌렀을 때
        LOGGER.warning('POST method')
        api = scrap_url(request)
        dict_return['api'] = api
    else:  # 새로고침을 했을 때
        LOGGER.warning('GET method')

    dict_return['form'] = form
    return render(request, 'scrap/main_view.html', dict_return)


def scrap_url(request):
    """
    URL을 스크래핑하는 함수.
    사용자의 버튼 클릭에 따라
        기존에 스크래핑된 것을 가져올 수도 있고,
        새로 스크래핑할 수도 있다.

    :param request: request
    :return: 스크래핑된 url의 데이터를 포함한 API
    """
    url = get_url_from_request(request)
    url = reconstitute_url(url)

    if 'action_scrap_cached' in request.POST:
        LOGGER.warning('Scrap Cached')
        if is_scrapped(url) is True:  # scrap된 적이 있는 url인지 확인
            LOGGER.warning("url info ALREADY exists")
            return get_api_from_database(url)

    LOGGER.warning('Scrap New')
    return get_api(url)


def reconstitute_url(original_url):
    """
    사용자가 입력한 url을 재구성하는 함수

    :param original_url: 사용자가 입력한 url
    :return: http 규약이 맞춰진 urㅣ
    """
    reconstituted_url = original_url
    reg = re.compile(r'^http://')
    if reg.match(original_url) is None:
        reconstituted_url = "http://" + original_url
    return reconstituted_url


def get_url_from_request(request):
    """
    뷰단에서 넘어온 request로부터 사용자가 입력한 url을 추출하는 함수

    :param request: 뷰단에서 넘어온 url
    :return: 사용자가 입력한 url
    """
    response = dict(request.POST)
    url = response['url'][0]
    return url


def is_scrapped(url):
    """
    url이 기존에 스크래핑됬는지의 여부를 확인하는 함수

    :param url: 사용자가 입력한 url
    :return: 데이터베이스 조회 결과가 있으면 True, 없으면 False 반환
    """
    s_url = ScrappedUrl.objects.filter(input_url=url)
    return len(s_url) != 0


def get_api(url):
    """
    클라이언트에 응답할 API를 형성하고 반환하는 함수

    :param url: 스크래핑할 url
    :return: 클라이언트에 응답할 API:
        title,
        url,
        type,
        image,
        description,
        scrapped_time,
        expiry_time
    """
    LOGGER.warning("Entry of get_api method")
    api = {}
    try:
        response = requests.get(url)
        LOGGER.warning("After request url")
        api = constitute_api(response)
        save_scrappedurl_object(api, url)
    except ConnectionError as err:
        LOGGER.error(err)

    return api


def constitute_api(response):
    """
    실제 API를 구성하는 함수

    :param response: url요청에 대한 응답
    :return: 스크래핑 API
    """
    html = response.text
    status_code = {'status_code': response.status_code}
    tags = get_tags(html)
    times = get_time_api()
    return dict(tags.items() | times.items() | status_code.items())


def get_tags(html):
    """
    스크래핑한 HTML로부터 원하는 태그를 얻는 함수

    :param html: 스크래핑한 url의 html
    :return: opengraph tags:
        og:title,
        og:url,
        og:type,
        og:image,
        og:description
    """
    LOGGER.warning("entry of get_tags method")
    soup = BeautifulSoup(html, "lxml")
    og_title = soup.find('meta', property='og:title')
    og_url = soup.find('meta', property='og:url')
    og_type = soup.find('meta', property='og:type')
    og_image = soup.find('meta', property='og:image')
    og_description = soup.find('meta', property='og:description')
    return {
        'title': og_title['content'] if og_title else "No meta title given",
        'url': og_url['content'] if og_url else "No meta url given",
        'type': og_type['content'] if og_type else "No meta type given",
        'image': og_image['content'] if og_image else "No meta image given",
        'description': og_description['content'] if og_description else "No meta description given",
    }


def get_time_api():
    """
    API에 들어갈 스크래핑된 시간과 만료 시간을 얻는 함수

    :return: 스크래핑된 시간, 만료 시간
    """
    scrapped_time = datetime.datetime.now()
    expiry_time = scrapped_time + datetime.timedelta(days=1)
    LOGGER.warning(scrapped_time.strftime("%Y-%m-%d %H:%M"))
    LOGGER.warning(expiry_time.strftime("%Y-%m-%d %H:%M"))
    return {
        'scrapped_time': scrapped_time,
        'expiry_time': expiry_time,
    }


def save_scrappedurl_object(api, input_url):
    """
    새로 스크래핑한 데이터를 데이터베이스에 저장하는 함수

    :param api: 스크래핑 API
    :param input_url: 사용자가 입력한 url
    :return:
    """
    url_object = ScrappedUrl(title=api['title'],
                             input_url=input_url,
                             url=api['url'],
                             type=api['type'],
                             image=api['image'],
                             description=api['description'],
                             status_code=api['status_code'],
                             scrapped_time=api['scrapped_time'],
                             expiry_time=api['expiry_time'])

    LOGGER.warning(url_object)
    url_object.save()


def get_api_from_database(url):
    """
    데이터베이스에서 캐싱된 스크래핑 API를 받아오는 함수

    :param url: 사용자가 입력한 url
    :return: 캐싱된 API
    """
    api_object = ScrappedUrl.objects.filter(input_url=url)
    LOGGER.warning(api_object)
    api_dict = list(api_object)[0]
    LOGGER.warning(api_dict)
    return {
        'title': api_dict.title,
        'url': api_dict.url,
        'type': api_dict.type,
        'image': api_dict.image,
        'description': api_dict.description,
        'scrapped_time': api_dict.scrapped_time,
        'expiry_time': api_dict.expiry_time,
    }
