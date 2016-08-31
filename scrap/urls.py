"""
urlpatterns는 url() 인스턴스 리스트여야만 한다
"""
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.main_view, name='main_view'),
]
