"""
requests: http 응답을 얻기 위함
"""
from django.test import TestCase
import requests


from .views import constitute_api
from .views import is_scrapped
from .views import reconstitute_url
from .views import get_api_from_database
from .views import save_scrappedurl_object
from .forms import UrlForm

# Create your tests here.


class ViewsTestCase(TestCase):
    """
    views.py에 있는 함수들을 테스트하는 클래스
    """
    def test_reconstitute_url(self):
        """
        reconstitute_url 함수를 테스트하는 함수

        :return:
        """
        url_1 = 'http://www.naver.com'
        url_2 = 'www.naver.com'
        url_3 = 'naver.com'

        res_1 = reconstitute_url(url_1)
        res_2 = reconstitute_url(url_2)
        res_3 = reconstitute_url(url_3)

        self.assertEqual(res_1, 'http://www.naver.com')
        self.assertEqual(res_2, 'http://www.naver.com')
        self.assertEqual(res_3, 'http://naver.com')

    def test_constitute_api(self):
        """
        constitute_api 함수를 테스트하는 함수

        :return:
        """
        url_1 = 'http://www.naver.com'
        res_1 = constitute_api(requests.get(url_1))

        self.assertNotEqual(res_1, {})

    def test_is_scrapped(self):
        """
        is_scrapped 함수를 테스트하는 함수

        :return:
        """
        url_1 = 'http://www.naver.com'
        url_2 = 'http://www.daum.net'

        api_1 = constitute_api(requests.get(url_1))
        save_scrappedurl_object(api_1, url_1)

        res_1 = is_scrapped(url_1)
        res_2 = is_scrapped(url_2)

        self.assertEqual(res_1, True)
        self.assertEqual(res_2, False)

    def test_get_url_from_request(self):
        """
        get_url_from_request 함수를 테스트하는 함수

        :return:
        """
        url = 'http://www.naver.com'
        form_data = {'url': url}
        form = UrlForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_get_api_from_database(self):
        """
        get_api_from_database 함수를 테스트하는 함수

        :return:
        """
        url_1 = 'http://www.naver.com'

        api_1 = constitute_api(requests.get(url_1))
        save_scrappedurl_object(api_1, url_1)

        res_1 = get_api_from_database(url_1)

        self.assertFalse(res_1, {})
