import functools

from django.db import models
from django.utils import timezone


class Crawl(models.Model):

    start = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    end = models.DateTimeField(blank=True, null=True)

    # Want the source PDF so we can analyze it
    json_results = models.FileField(
        max_length=1024,
        blank=False,
        null=False,
        upload_to="crawls",
    )
