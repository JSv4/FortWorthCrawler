import functools

from django.db import models
from django.utils import timezone


from fort_worth_crawler.shared.defaults import NullableJSONField
from fort_worth_crawler.shared.fields import jsonfield_default_value
from fort_worth_crawler.shared.paths import calc_pdf_file_path


class Document(models.Model):

    class Meta:
        # documents should have a unique repository id, but we want to be able to version up for changes to existing
        # docs (so we don't lose them). Making the two unique together lets us do this.
        constraints = [
            models.UniqueConstraint(
                fields=['repository_unique_id', 'local_version'],
                name='unique_1'
            )
        ]

    # Title for convenience
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=False, blank=True, default="")
    page_count = models.IntegerField(null=False, blank=False, default=0)
    tagged_counterparty = models.CharField(max_length=1024, null=True, blank=True)
    project_number = models.CharField(max_length=1024, null=True, blank=True)

    # Want to traack the unique id in the repository
    repository_unique_id = models.CharField(max_length=1024, null=False, blank=False)
    # If remote doc is updated... create new version, don't overwrite
    local_version = models.IntegerField(default=1, blank=False, null=False)

    # Want to be able to get back to the source URL (if possible)
    repository_url = models.CharField(max_length=1024, null=True, blank=True)

    # If there is some kind of path/folder structure, provide it
    repository_folder_path = models.CharField(max_length=1024, null=True, blank=True)

    # Provides some flexibility on model metadata storage, though some fields are be broken out (like counterparty)
    custom_meta = NullableJSONField(
        default=jsonfield_default_value,
        null=True
    )

    # Scraped document entry json which we used to scan
    source_json = NullableJSONField(
        default=jsonfield_default_value,
        null=True
    )

    # Tracking Variables, so we know last time this was updated on this system (and can make changes if needed)
    first_scraped = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    last_updated_locally = models.DateTimeField(auto_now=True, blank=False, null=False)
    last_updated_on_remote = models.DateTimeField(blank=False, null=False)

    # Want the source PDF so we can analyze it
    pdf_file = models.FileField(
        max_length=1024,
        blank=False,
        null=False,
        upload_to=functools.partial(calc_pdf_file_path, sub_folder="pdf_files"),
    )
