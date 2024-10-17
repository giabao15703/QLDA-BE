import os
import uuid

from django.db import models
from django.utils.text import slugify
from model_utils.models import TimeStampedModel

def banner_directory_path(instance, filename):
    return os.path.join("banner", "{}.{}".format("banner" + "_" + slugify(instance.name) + "_" + str(uuid.uuid4()), filename.split(".")[-1]))

def banner_mobile_directory_path(instance, filename):
    return os.path.join("banner", "{}.{}".format("banner_mobile" + "_" + slugify(instance.name) + "_" + str(uuid.uuid4()), filename.split(".")[-1]))

class BannerGroup(models.Model):
    item_code = models.CharField(max_length=250, null=False, blank=False, unique=True)
    name = models.CharField(max_length=250)
    description = models.CharField(max_length=10000, null=True, blank=True)
    
    class Meta:
        db_table = "banner_banner_group"

class Banner(TimeStampedModel, models.Model):
    group = models.ForeignKey(BannerGroup, on_delete=models.CASCADE, related_name="banners", null=True, blank=True)
    name = models.CharField(max_length=500, null=True, blank=True)
    file = models.FileField(upload_to=banner_directory_path, null=True, blank=True)
    file_mobile = models.FileField(upload_to=banner_mobile_directory_path, null=True, blank=True)
    link = models.CharField(max_length=1000, null=True, blank=True)
    sort_order = models.IntegerField(default=0)
    description = models.CharField(max_length=10000, null=True, blank=True)
    animation = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = "banner_banner"
