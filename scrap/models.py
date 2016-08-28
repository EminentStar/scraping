from django.db import models
from django.utils import timezone

# Create your models here.


class ScrappedUrl(models.Model):
    title = models.CharField(max_length=200)
    url = models.CharField(max_length=2000)
    type = models.CharField(max_length=50)
    image = models.CharField(max_length=2000)
    description = models.TextField()
    status_code = models.IntegerField()
    scrapped_time = models.DateTimeField()
    expiry_time = models.DateTimeField()

    def __unicode__(self):
        return self.url
