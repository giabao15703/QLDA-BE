from django.db import models

class DeliveryError(models.TextChoices):
    DELIVERY_01 = "Invalid token"
    DELIVERY_02 = "No permission"
    DELIVERY_03 = "Pick up city does not exist"
    DELIVERY_04 = "Destination city does not exist"
    DELIVERY_05 = "Input field is invalid"
    DELIVERY_06 = "Failed to create shipping fee"
    DELIVERY_07 = "Shipping fee is not exist"
    DELIVERY_08 = "Item code must be 6 characters"
    DELIVERY_09 = "Failed to create transporter"
    DELIVERY_10 = "Transporter is not exist"
    DELIVERY_11 = "City code does not exist"
    DELIVERY_12 = "Failed to create delivery responsible"
    DELIVERY_13 = "Delivery responsible is not exist"

