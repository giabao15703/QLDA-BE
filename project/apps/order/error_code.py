from django.db import models

class OrderError(models.TextChoices):
    ORDER_01 = "Order does not exist"

