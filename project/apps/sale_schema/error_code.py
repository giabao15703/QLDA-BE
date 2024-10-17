from django.db import models

class SaleSchemaError(models.TextChoices):
    SALE_SCHEMA_01 = "Percentage must be more than 0% or less than 100%"
    SALE_SCHEMA_02 = "The min-max value you entered is not illega"
    SALE_SCHEMA_03 = "The min-max value you entered is duplicated"
    SALE_SCHEMA_04 = "Min value must be less than or equal max value"
    SALE_SCHEMA_05 = "You do not have permission to perform this action"
