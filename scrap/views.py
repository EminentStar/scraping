from django.contrib import messages
from django.shortcuts import render
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
        form = UrlForm()
        return render(request, 'scrap/main_view.html', {'form': form, 'api': api})
    else:
        logger.warning('GET method') # 새로고침을 했을 때
        form = UrlForm()
    return render(request, 'scrap/main_view.html', {'form': form})


def scrap_url(request):
    url = get_url_from_request(request)
    url = reconstitute_url(url)
    if is_scrapped(url) is False: # scrap된 적이 있는 url인지 확인
        return get_api(url)
    else: # Database에 캐싱되있던 api데이터를 가져온다
        logger.warning("url info ALREADY exists")
        return get_api_from_database(url)


def reconstitute_url(original_url):
    reconstituted_url = original_url
    reg = re.compile(r'^http://')
    if reg.match(original_url) is None:
        reconstituted_url = "http://" + original_url
    return reconstituted_url


def get_url_from_request(request):
    r = dict(request.POST)
    url = r['url'][0]
    return url


def is_scrapped(url):
    s_url = ScrappedUrl.objects.filter(input_url=url)
    return len(s_url) != 0


def get_api(url):
    logger.warning("Entry of get_api method")
    api = {}
    try:
        r = requests.get(url)
        logger.warning("After request url")
        api = constitute_api(r)
        save_scrappedurl_object(api, url)
    except ConnectionError as e:
        logger.error(e)
    finally:
        return api


def constitute_api(response):
    html = response.text
    status_code = {'status_code': response.status_code}
    tags = get_tags(html)
    times = get_time_api()
    return dict(tags.items() | times.items() | status_code.items())


def get_tags(html):
    logger.warning("entry of get_tags method")
    soup = BeautifulSoup(html, "lxml")
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
    logger.warning(scrapped_time.strftime("%Y-%m-%d %H:%M"))
    logger.warning(expiry_time.strftime("%Y-%m-%d %H:%M"))
    return {
        'scrapped_time': scrapped_time,
        'expiry_time': expiry_time,
    }


def save_scrappedurl_object(api, input_url):
    url_object = ScrappedUrl(title=api['title'],
                             input_url=input_url,
                             url=api['url'],
                             type=api['type'],
                             image=api['image'],
                             description=api['description'],
                             status_code=api['status_code'],
                             scrapped_time=api['scrapped_time'],
                             expiry_time=api['expiry_time'])

    logger.warning(url_object)
    url_object.save()


def get_api_from_database(url):
    api_object = ScrappedUrl.objects.filter(input_url=url)
    logger.warning(api_object)
    api_dict = list(api_object)[0]
    logger.warning(api_dict)
    return {
        'title': api_dict.title,
        'url': api_dict.url,
        'type': api_dict.type,
        'image': api_dict.image,
        'description': api_dict.description,
        'scrapped_time': api_dict.scrapped_time,
        'expiry_time': api_dict.expiry_time,
    }





