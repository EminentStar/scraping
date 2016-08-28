from django.test import TestCase
import requests


from .views import constitute_api
from .views import is_scrapped
from .views import reconstitute_url
from .views import get_api
from .views import get_api_from_database
from .views import get_url_from_request
from .views import save_scrappedurl_object
from .views import scrap_url
from .forms import UrlForm

# Create your tests here.


class ViewsTestCase(TestCase):
    def test_reconstitute_url(self):
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
        url_1 = 'http://www.naver.com'
        res_1 = constitute_api(requests.get(url_1))

        self.assertNotEqual(res_1, {})

    def test_is_scrapped(self):
        url_1 = 'http://www.naver.com'
        url_2 = 'http://www.daum.net'

        api_1 = constitute_api(requests.get(url_1))
        save_scrappedurl_object(api_1, url_1)

        res_1 = is_scrapped(url_1)
        res_2 = is_scrapped(url_2)

        self.assertEqual(res_1, True)
        self.assertEqual(res_2, False)

    def test_get_url_from_request(self):
        url = 'http://www.naver.com'
        form_data = {'url': url}
        form = UrlForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_get_api_from_database(self):
        url_1 = 'http://www.naver.com'

        api_1 = constitute_api(requests.get(url_1))
        save_scrappedurl_object(api_1, url_1)

        res_1 = get_api_from_database(url_1)

        self.assertFalse(res_1, {})
