from django.db import models
from django.contrib.auth.models import User, AbstractUser
# SuperUserInformation
# User: Jose
# Email: training@pieriandata.com
# Password: testpassword

# Create your models here.
class CustomUser(AbstractUser):

    is_active = models.BooleanField(default=True)

    is_customer = models.BooleanField(default=False)
    is_staffInChina = models.BooleanField(default=False)
    is_staffInUSA = models.BooleanField(default=False)
    is_supervisor = models.BooleanField(default=True)

    USER_TYPE_CHOICES = (
      (1, 'customer'),
      (2, 'staffInChina'),
      (3, 'staffInUSA'),
      (4, 'supervisor'),
    )

    user_type = models.PositiveSmallIntegerField(choices=USER_TYPE_CHOICES, default=4)

    def __str__(self):
        return self.email

