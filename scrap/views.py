from django.shortcuts import render
import datetime
import logging
import requests
from bs4 import BeautifulSoup
from pprint import pprint


from .forms import UrlForm

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


def get_url_from_request(request):
    r = dict(request.POST)
    url = r['url'][0]
    return url


def fetch_url(url):
    r = requests.get(url)
    return r.text


def get_tags(html):
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


def get_etc_api():
    scrapped_time = datetime.datetime.now()
    expiry_time = scrapped_time + datetime.timedelta(days=1)
    scrapped_time = scrapped_time.strftime("%B %d, %Y")
    expiry_time = expiry_time.strftime("%B %d, %Y")
    print(scrapped_time)
    print(expiry_time)
    return {
        'scrapped_time': scrapped_time,
        'expiry_time': expiry_time,
    }


def scrap_url(request):
    url = get_url_from_request(request)
    html = fetch_url(url)
    tags = get_tags(html)
    times = get_etc_api()
    return dict(tags.items() | times.items())

