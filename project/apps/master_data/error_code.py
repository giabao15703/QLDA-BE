from django.db import models

class MasterDataError(models.TextChoices):
    MASTER_DATA_01 = "Item Code must be less than 3 characters"
    MASTER_DATA_02 = "Item Code must be 3 characters"
    MASTER_DATA_03 = "Item Code must be 4 characters"
    MASTER_DATA_04 = "Item Code must be 5 characters"
    MASTER_DATA_05 = "Promotion must be from 1% to 100%'"
    MASTER_DATA_06 = "Promotion Program is already exists"
    MASTER_DATA_07 = "Item Code must be less than 4 characters"
    MASTER_DATA_08 = "Item Code must be less than 5 characters"
    MASTER_DATA_09 = "Item Code must be less than 6 characters"
    MASTER_DATA_10 = "Commission must be from 1% to 100%"
    MASTER_DATA_11 = "Coupon Program is already exists"
    MASTER_DATA_12 = "Valid To must be later than Valid From"
    MASTER_DATA_13 = "Item_code is already exists"
    MASTER_DATA_14 = "Invalid token"
    MASTER_DATA_15 = "Promotion is required"
    MASTER_DATA_16 = "Country doesn't exist"
    MASTER_DATA_17 = "City doesn't exist"

