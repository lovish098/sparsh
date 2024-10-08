from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    pname = models.CharField(max_length=200 , null=True, blank=True)
    pmobile = models.CharField(max_length=200 , null=True, blank=True)
    pemail = models.CharField(max_length=200 , null=True, blank=True)
    paddress = models.CharField(max_length=200 , null=True, blank=True)    
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.pname

    class Meta:
        order_with_respect_to = 'user'
