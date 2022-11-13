from django.contrib import admin

from .models import Crawl

@admin.register(Crawl)
class CrawlAdmin(admin.ModelAdmin):
    pass
