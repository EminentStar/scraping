"""
django의 form을 정의
"""
from django import forms


class UrlForm(forms.Form):
    """
    사용자가 스크래핑을 원하는 url을 입력하는 폼
    """
    url = forms.CharField(label='', max_length=2000)
