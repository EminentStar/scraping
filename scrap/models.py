"""
django의 model을 정의
"""
from django.db import models

# Create your models here.


class ScrappedUrl(models.Model):
    """
    스크래핑한 url의 API 정보 및 사용자 입력 url을 저장하는 model
    """
    title = models.CharField(max_length=200)
    input_url = models.CharField(max_length=2000)
    url = models.CharField(max_length=2000)
    type = models.CharField(max_length=50)
    image = models.CharField(max_length=2000)
    description = models.TextField()
    status_code = models.IntegerField(default=200)
    scrapped_time = models.DateTimeField()
    expiry_time = models.DateTimeField()

    def __unicode__(self):
        return self.input_url
