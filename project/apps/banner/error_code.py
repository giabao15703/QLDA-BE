from django.db import models

class BannerError(models.TextChoices):
    BANNER_01 = "Banner does not exists"
    BANNER_02 = "Invalid token"
    BANNER_03 = "Banner group with Item code already exists."
    BANNER_04 = "Sort order must not be duplicated"
    BANNER_05 = "Banner group with this Site and Item code already exists."
    BANNER_06 = "Banner group does not exists"