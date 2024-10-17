import os
import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.text import slugify
from model_utils.models import TimeStampedModel

User = get_user_model()

def gallery_directory_path(instance, filename):
    return os.path.join(str(instance.user.id),'gallery', "{}.{}".format(slugify(filename.split(".")[0]) + "_" + str(uuid.uuid4()), filename.split('.')[-1]))

class Gallery(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="gallery")
    name = models.CharField(max_length=200, null=True, blank=True)
    file = models.FileField(upload_to=gallery_directory_path)
    description = models.CharField(max_length=10000, null=True, blank=True)

    class Meta:
        db_table = "galleries_gallery"
