import os
import re 
from apps.sale_schema.models import ProfileFeaturesBuyer, ProfileFeaturesSupplier
from django.db import models

# Create your models here.
def video_directory_path(instance, filename):
    name  = instance.name
    string = (re.sub(r'\W+', ' ', name))
    name = string.replace(" ", "_")
    return os.path.join('user_guide', "{}.{}".format(name, filename.split('.')[-1]))

ROLE_CHOICES = (
    (1, 'admin'),
    (2, 'buyer'),
    (3, 'supplier')
)

class Modules(models.Model):
    name = models.CharField(max_length=255)
    status = models.BooleanField(null=True, default=True)
    role  = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, null=False, default=1)
    class Meta:
        db_table = 'user_guide_modules'

class Courses(models.Model):
    name = models.CharField(max_length=255)
    video = models.FileField(upload_to=video_directory_path,null=True)
    modules = models.ForeignKey(Modules, on_delete=models.CASCADE)
    status = models.BooleanField(null=True, default=True)
    role  = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, null=False, default=1)
    class Meta:
        db_table = 'user_guide_coures'
        
class CoursesProfileFeaturesBuyer(models.Model):
    courses = models.ForeignKey(Courses, on_delete=models.CASCADE)
    profile_features = models.ForeignKey(ProfileFeaturesBuyer, on_delete=models.CASCADE)
    class Meta:
        db_table = 'user_guide_coures_profile_features_buyer'

class CoursesProfileFeaturesSupplier(models.Model):
    courses = models.ForeignKey(Courses, on_delete=models.CASCADE)
    profile_features = models.ForeignKey(ProfileFeaturesSupplier, on_delete=models.CASCADE)
    class Meta:
        db_table = 'user_guide_coures_profile_features_supplier'