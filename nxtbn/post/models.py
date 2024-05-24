from django.db import models
from django.utils import timezone

from nxtbn.core.models import AbstractBaseModel, AbstractSEOModel, PublishableModel, AbstractBaseUUIDModel


from django.utils import timezone
from nxtbn.users.models import User


class Category(AbstractBaseModel, AbstractSEOModel):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Post(PublishableModel, AbstractSEOModel):
    name = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)

    def __str__(self):
        return self.title
