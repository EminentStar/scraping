from django.shortcuts import render
from django.utils import timezone
import datetime
import logging
import re
import requests
from bs4 import BeautifulSoup


from .forms import UrlForm
from .models import ScrappedUrl

# Create your views here.

logger = logging.getLogger(__name__)


def main_view(request):
    if request.method == 'POST': # 웹 스크래핑 버튼을 눌렀을 때
        logger.warning('POST method')
        """input 태그의 url 스크래핑을 시도한다."""
        api = scrap_url(request)
        print("api:::")
        print(api)
        form = UrlForm()
        return render(request, 'scrap/main_view.html', {'form': form, 'api': api})
    else:
        logger.warning('GET method') # 새로고침을 했을 때
        form = UrlForm()
    return render(request, 'scrap/main_view.html', {'form': form})


def get_url_from_request(request):
    r = dict(request.POST)
    url = r['url'][0]
    return url


def get_tags(html):
    logger.warning("entry of get_tags method")
    soup = BeautifulSoup(html)
    title = soup.find('meta', property='og:title')
    url = soup.find('meta', property='og:url')
    type = soup.find('meta', property='og:type')
    image = soup.find('meta', property='og:image')
    description = soup.find('meta', property='og:description')
    return {
        'title': title['content'] if title else "No meta title given",
        'url': url['content'] if url else "No meta url given",
        'type': type['content'] if type else "No meta type given",
        'image': image['content'] if image else "No meta image given",
        'description': description['content'] if description else "No meta description given",
    }


def get_time_api():
    scrapped_time = datetime.datetime.now()
    expiry_time = scrapped_time + datetime.timedelta(days=1)
    logger.warning(scrapped_time)
    logger.warning(expiry_time)
    return {
        'scrapped_time': scrapped_time,
        'expiry_time': expiry_time,
    }


def get_api(url):
    logger.warning("Entry of get_api method")
    api = {}
    try:
        r = requests.get(url)
        logger.warning("After request url")
        html = r.text
        status_code = {'status_code': r.status_code}
        tags = get_tags(html)
        times = get_time_api()
        api = dict(tags.items() | times.items() | status_code.items())
    except ConnectionError as e:
        logger.error(e)
    finally:
        return api


def scrap_url(request):
    url = get_url_from_request(request)
    if is_scrapped(url) is False: # scrap된 적이 있는 url인지 확인
        return get_api(url)
    else: # Database에 캐싱되있던 api데이터를 가져온다
        return get_api_from_database(url)


def get_api_from_database(url):
    api_object = ScrappedUrl.objects.filter(url=url)
    return {
        'title': api_object.title,
        'url': api_object.url,
        'type': api_object.type,
        'image': api_object.image,
        'description': api_object.description,
        'scrapped_time': api_object.scrapped_time,
        'expiry_time': api_object.expiry_time,
    }


def is_scrapped(url):
    s_url = ScrappedUrl.objects.filter(url=url)
    return s_url is True
