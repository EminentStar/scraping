import datetime
import logging
import re
import redis
import requests
from bs4 import BeautifulSoup
import json

from .models import ScrappedUrl
from . import log_generator

HOST_IDX = 0
PORT_IDX = 1

LOGGER = logging.getLogger(__name__)

conns = {}


def scrap_url_cached(request, chashing):
    """
    (분산 캐시 버전)URL을 스크래핑하는 함수.

    :param request: request
    :return: 스크래핑된 url의 데이터를 포함한 API
    """
    url = get_url_from_request(request)
    url = reconstitute_url(url)

    cached_node = chashing.find_node_with_value(url)
    
    if 'action_scrap_cached' in request.POST:
        scrapped_data = is_scrapped_from_caches(url, cached_node)
        if scrapped_data:  # scrap된 적이 있는 url인지 확인
            # scrapped_data를 스트링에서 json화시킨다.
            api = eval(scrapped_data)
            return api

    #새로운 스크랩
    return get_api_cache(url, chashing)


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
        if is_scrapped(url):  # scrap된 적이 있는 url인지 확인
            return get_api_from_database(url)

    #새로운 스크랩
    return get_api(url)


def is_scrapped_from_caches(url, cached_node):
    """
    url이 분산 캐시에 스크래핑되어있는지 검색하는 함수
    
    :param url: 사용자가 입력한 url
    :return: 캐싱되어있으면 url API 데이터(JSON), 없으면 None을 반환함.
    """

    node_client = check_cache_server_list(conns, cached_node)

    scrapped_data = get_data_from_cache(url, node_client)
    #if scrapped_data:
        #LOGGER.info(log_generator.cache_access_log_json(cached_node[HOST_IDX], 'GET', url))
        
    return scrapped_data


def get_url_from_request(request):
    """
    뷰단에서 넘어온 request로부터 사용자가 입력한 url을 추출하는 함수

    :param request: 뷰단에서 넘어온 url
    :return: 사용자가 입력한 url
    """ 
    
    if request.method == 'POST':
        response = dict(request.POST) 
        url = response['url'][0]
    elif request.method == 'GET':
        url = request.GET['url']

    return url


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


def get_api_cache(url, chashing):
    """
    (분산 캐시 버전)클라이언트에 응답할 API를 형성하고 반환하는 함수

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
    curr_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    api = {}
    is_error = False
    curr_time = log_generator.get_curr_time()

    try:
        response = requests.get(url)
        api = constitute_api(response)
        # api 문자열을 알맞은 레디스 서버에 캐싱한다.
        api_str = str(api)
        save_data_to_cache(url, api_str, chashing)        
    except ConnectionError as err:
        # 로그 추가
        #LOGGER.error(log_generator.scrap_error_log_json(curr_time, url, err))
        print(err)
        is_error = True
    
    #LOGGER.info(log_generator.scrap_request_log_json(curr_time, url, is_error))
    return api


def get_data_from_cache(url, node_client):
    data = node_client.get(url)
    if data:
        data = data.decode()
    return data


def save_data_to_cache(url, api_str, chashing):
    """
    (분산 캐시 버전)적정 캐시 서버에 api 데이터를 저장한다.
    """
    cached_node = chashing.find_node_with_value(url)
    url_hash = chashing._hash(url)[0]

    node_client = check_cache_server_list(conns, cached_node)

    set_data_to_cache(url_hash, api_str, node_client)
    #LOGGER.info(log_generator.cache_access_log_json(cached_node[HOST_IDX], 'SET', url))


def check_cache_server_list(conns, cached_node):
    if cached_node[HOST_IDX] in conns:
        node_client = conns[cached_node[HOST_IDX]]
    else:
        node_client = redis.StrictRedis(host = cached_node[HOST_IDX], port = cached_node[PORT_IDX])
        conns[cached_node[HOST_IDX]] = node_client
    return node_client



def set_data_to_cache(url_hash, api_str, node_client):
    node_client.set(url_hash, api_str)
    

def is_scrapped(url):
    """
    url이 기존에 스크래핑됬는지의 여부를 확인하는 함수

    :param url: 사용자가 입력한 url
    :return: 데이터베이스 조회 결과가 있으면 True, 없으면 False 반환
    """
    s_url = ScrappedUrl.objects.filter(input_url=url)
    return len(s_url) != 0


def get_api_from_database(url):
    """
    데이터베이스에서 캐싱된 스크래핑 API를 받아오는 함수

    :param url: 사용자가 입력한 url
    :return: 캐싱된 API
    """
    api_object = ScrappedUrl.objects.filter(input_url=url)
    api_dict = list(api_object)[0]
    return {
        'title': api_dict.title,
        'url': api_dict.url,
        'type': api_dict.type,
        'image': api_dict.image,
        'description': api_dict.description,
        'scrapped_time': api_dict.scrapped_time,
        'expiry_time': api_dict.expiry_time,
    }


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
    api = {}
    try:
        response = requests.get(url)
        api = constitute_api(response)
        save_scrappedurl_object(api, url)
    except ConnectionError as err:
       #LOGGER.error(log_generator.other_errors_log_json(err))
       print(err)

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

    url_object.save()


