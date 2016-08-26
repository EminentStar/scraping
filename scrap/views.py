from django.shortcuts import render
import logging

from .forms import UrlForm

# Create your views here.

logger = logging.getLogger(__name__)


def main_view(request):
    if request.method == 'POST': # 웹 스크래핑 버튼을 눌렀을 때
        logger.warning('POST method')
        """input 태그의 url 스크래핑을 시도한다."""
    else:
        logger.warning('GET method') # 새로고침을 했을 때
        form = UrlForm()
    return render(request, 'scrap/main_view.html', {'form': form})

