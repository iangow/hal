from django.db import models
from django.contrib.auth.models import User
from jsonfield import JSONField
# import reversion


# @reversion.register
class Annotation(models.Model):
    quote = models.TextField()
    ranges = JSONField()
    text = models.TextField(blank=True)
    uri = models.TextField()
    user = models.ForeignKey(User, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
