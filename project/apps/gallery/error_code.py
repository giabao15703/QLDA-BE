from django.db import models

class GalleryError(models.TextChoices):
    GALLERY_01 = "Gallery does not exists"
    GALLERY_02 = "Invalid token"