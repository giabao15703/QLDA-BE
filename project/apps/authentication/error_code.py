from django.db import models


class AuthencationError(models.TextChoices):
    AUTH_01 = "The User ID or password is incorrect."
    AUTH_02 = "Please provide both username and password"
    AUTH_03 = "Account has been disabled"
    AUTH_04 = "Please provide token"
    AUTH_05 = "Invalid Credentials"
    AUTH_06 = "Please provide username"
    AUTH_07 = "Please provide email"
    AUTH_08 = "Username and Email are not match!"
    AUTH_09 = "Token is not exists"
    AUTH_10 = "Please provide new password"
    AUTH_11 = "Password must be at least 6 characters"
    AUTH_12 = "Password and Confirm Password does not match"
    AUTH_13 = "Token is not valid"
    AUTH_14 = "User is not exists"
    AUTH_15 = "Password and Confirm password are not match"
    AUTH_16 = "Invalid token"
    AUTH_17 = "Old Password is incorrect"
    AUTH_18 = "User can only login to one device the same time"
    AUTH_19 = "Email already exists in system"

