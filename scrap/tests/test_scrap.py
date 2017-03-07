from django.test import TestCase
import requests


from scrap.scrap import reconstitute_url
from scrap.scrap import is_scrapped
from scrap.scrap import constitute_api 
from scrap.scrap import get_api_from_database 
from scrap.scrap import save_scrappedurl_object
from scrap.scrap import is_scrapped
from scrap.scrap import get_api_from_database


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
   
    def test_is_scrapped(self):
        url = 'http://www.test.com'
        response = is_scrapped(url)
        self.assertEquals(response, False)


    def test_get_api_from_database(self):
        url = 'http://www.test.com'
        response = get_api_from_database(url)
        print(response)
        self.assertEquals(response, {'error':'NoExists'})



