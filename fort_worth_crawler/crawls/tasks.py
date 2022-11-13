import json

from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile

from config import celery_app

from fort_worth_crawler.crawls.models import Crawl

from fort_worth_crawler.api.client import crawl_directory_recursively, root_contract_folder_id

User = get_user_model()


@celery_app.task()
def get_document_list_task() -> list[str]:
    """
    Task to crawl the Fort Worth repo API and produce a list of documents... these will then be stored as a daily
    crawl and analyzed to see if any of them have a date modified AFTER what we have for the same doc in our database (
    or are missing from our database entirely). Those will be synced and downloaded. Others will be discarded.

    :return: List of "entryIds" to request document metadata and pdfs for
    """
    crawl = Crawl.objects.create()

    full_recursive_results = crawl_directory_recursively(
        repo="City-Secretary",
        folder_id=root_contract_folder_id
    )

    end_time = timezone.now()
    crawl.end = end_time
    json_file = ContentFile(json.dumps(full_recursive_results, indent=4).encode('utf-8'))
    crawl.json_results.save(f"crawl_{end_time.timestamp()}.json", json_file)
    crawl.save()

    return full_recursive_results
