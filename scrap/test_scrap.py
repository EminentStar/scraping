from django.test import TestCase
import requests


from .scrap import reconstitute_url
from .scrap import is_scrapped
from .scrap import constitute_api 
from .scrap import get_api_from_database 
from .scrap import save_scrappedurl_object


class ScrapTests(TestCase):
    """
    scrap.py에 있는 함수들을 테스트하는 클래스
    """
        
    def test_reconstitute_url(self):
        """
        reconstitute_url 함수를 테스트하는 함수

        :return:
        """
        url_1 = 'http://www.naver.com'
        url_2 = 'www.naver.com'
        url_3 = 'naver.com'

    
        response_1 = reconstitute_url(url_1)
        response_2 = reconstitute_url(url_2)
        response_3 = reconstitute_url(url_3)

        self.assertEquals(response_1, 'http://www.naver.com')
        self.assertEquals(response_2, 'http://www.naver.com')
        self.assertEquals(response_3, 'http://naver.com')


    def test_constitute_api(self):
        """
        constitute_api 함수를 테스트하는 함수

        :return:
        """
        url_1 = 'http://www.naver.com'
        response_1 = constitute_api(requests.get(url_1))

        self.assertNotEqual(response_1, {})
        

