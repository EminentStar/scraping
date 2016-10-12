"""
datetime: 시간파악을 위함
logging: 로깅
re: 정규표현식 검색을 위함
requests: http 요청을 하기 위함
BeautifulSoup: 웹 스크래핑을 위함
"""
from django.shortcuts import render
import redis
import logging
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.http import JsonResponse


from .forms import UrlForm
from .consistent_hashing import ConsistentHashingPartitioning
from .scrap import scrap_url_cached
from . import log_generator

# Create your views here.
LOGGER = logging.getLogger(__name__)

IP = 'localhost'
PORT_1 = 6379
PORT_2 = 6380
PORT_3 = 6381

redis_client1 = redis.StrictRedis(host = IP, port = PORT_1)
redis_client2 = redis.StrictRedis(host = IP, port = PORT_2)
redis_client3 = redis.StrictRedis(host = IP, port = PORT_3)

nodelist = []
nodelist.append((IP, str(PORT_1)))
nodelist.append((IP, str(PORT_2)))
nodelist.append((IP, str(PORT_3)))

vnode_counts = 40 

chashing = ConsistentHashingPartitioning(nodelist, vnode_counts)


def main_view(request):
    """
    애플리케이션의 메인 뷰.

    POST:param request: 뷰단의 request
    POST:return: 스크래핑된 url 데이터를 포함한 main_view.html이 렌더링된 것을 리턴

    GET:param request: request
    GET:return: 새로고침된 main_view.html이 렌더링된 것을 리턴
    """
    print("main_view") 
    dict_return = {}
    form = UrlForm()
    
    LOGGER.info(log_generator.http_request_log_json(request))
    if request.method == 'POST':  # 웹 스크래핑 버튼을 눌렀을 때
        api = scrap_url_cached(request, chashing)
        dict_return['api'] = api

    dict_return['form'] = form
    return render(request, 'scrap/main_view.html', dict_return)


@csrf_exempt
def apitest(request):
    api = scrap_url_cached(request, chashing)
    dict_return = api
    return JsonResponse(dict_return)
