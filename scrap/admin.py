"""
admin에 ScrappedUrl model을 등록함
"""
from django.contrib import admin
from .models import ScrappedUrl

# Register your models here.

admin.site.register(ScrappedUrl)
