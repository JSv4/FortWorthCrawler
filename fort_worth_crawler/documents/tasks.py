#  Copyright (C) 2022  John Scrudato / Gordium Knot Inc. d/b/a OpenSource.Legal
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
import time
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.

#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
from datetime import datetime

from django.core.files.base import ContentFile
from django.utils import timezone
from django.db import transaction
from django.contrib.auth import get_user_model

from fort_worth_crawler.api.client import download_bulk_pdfs, get_bulk_pdf_download_progress, request_bulk_pdf_export, \
    get_document_metadata
from fort_worth_crawler.documents.models import Document

from config import celery_app

User = get_user_model()


@celery_app.task()
def filter_document_jsons_to_new_and_newly_modified(document_jsons: list[dict]) -> list[int]:
    """
    Async post-processing task. Given the document json from the crawler, check that they're not in the database (by
    looking up the entryId) or, if they are, that the date modified on the remote server is NEWER than what we have in
    our database.

    :return: List of Document model ids we need to request docs for.
    """

    entry_id_set = set()
    doc_ids_to_process = []

    for index, document_json in enumerate(document_jsons):

        print(f"{index})\t{document_json}")

        existing_entries = Document.objects.filter(
            repository_unique_id=f"{document_json['entryId']}",
            local_version=1
        ).order_by('-last_updated_locally')
        print(f"\t{existing_entries.count()} docs with repo id {document_json['entryId']}")

        remote_last_updated_date_string = document_json['data'][10]
        remote_last_updated_datetime = timezone.make_aware(datetime.strptime(
            remote_last_updated_date_string,
            '%m/%d/%Y %I:%M:%S %p'
        ))

        entry_id_set.add(f"{document_json['entryId']}")

        # If document doesn't exist... create it
        if existing_entries.count() == 0:
            print("\tExisting entry count is 0")
            with transaction.atomic():
                new_doc = Document.objects.create(
                    title=document_json['name'],
                    repository_unique_id=f"{document_json['entryId']}",
                    local_version=1,
                    last_updated_on_remote=remote_last_updated_datetime,
                    source_json=document_json
                )
            doc_ids_to_process.append(new_doc.id)

        # IF it does exist, check if remote is newer, and, if so, upversion
        else:
            latest_entry = existing_entries[0]
            print(f"\tExisting entry count is > 0... latest entry id is {latest_entry.repository_unique_id} with last modified "
                  f"{latest_entry.last_updated_on_remote}... compare to current json of {remote_last_updated_datetime}")
            if latest_entry.last_updated_on_remote < remote_last_updated_datetime:
                print(f"\tCREATE NEW VERSION...")
                with transaction.atomic():
                    new_doc = Document.objects.create(
                        title=document_json['name'],
                        repository_unique_id=f"{document_json['entryId']}",
                        local_version=latest_entry.local_version+1,
                        last_updated_on_remote=remote_last_updated_datetime,
                        source_json=document_json
                    )
                doc_ids_to_process.append(new_doc.id)
            else:
                print(f"\tDocument with entryId {document_json['entryId']} already up-to-date in database")

    print(f"UNIQUE ENTRY IDS: {len(entry_id_set)}")

    return doc_ids_to_process


@celery_app.task()
def fetch_document_pdf_and_metadata(document_pk: int):

    print(f"Fetching doc data for database entry {document_pk}")

    doc_obj = Document.objects.get(pk=document_pk)

    print("Fetch metadata...")
    metadata = get_document_metadata(doc_obj.repository_unique_id)
    print(f"Fetched: {metadata}")

    attr_array = metadata['metadata']['fInfo']
    counterparty = list(filter(lambda x: x['name'] == 'Vendor', attr_array))[0]['values'][0]
    description = list(filter(lambda x: x['name'] == 'Subject', attr_array))[0]['values'][0]
    project_number = list(filter(lambda x: x['name'] == 'Project Number/ID', attr_array))[0]['values'][0]

    print(f"Initiate PDF download")
    bulk_download_token = request_bulk_pdf_export(entry_ids=[int(doc_obj.repository_unique_id)])
    print(f"Download token: {bulk_download_token}")
    download_status = get_bulk_pdf_download_progress(token=bulk_download_token)
    print(f"Download status: {download_status}")
    bulk_download_finished = download_status['finished']

    while not bulk_download_finished:
        print(f"Document pf {document_pk} download status: {download_status}")
        download_status = get_bulk_pdf_download_progress(token=bulk_download_token)
        bulk_download_finished = download_status['finished']
        time.sleep(3)

    doc_obj.custom_meta = metadata
    doc_obj.tagged_counterparty = counterparty
    doc_obj.description = description
    doc_obj.project_number = project_number
    doc_obj.page_count = metadata['pageCount']
    doc_obj.repository_folder_path = metadata['metadata']['path']
    doc_obj.save()

    pdf_file = ContentFile(download_bulk_pdfs(bulk_download_token=bulk_download_token))
    doc_obj.pdf_file.save(f"{metadata['name']}.pdf", pdf_file)

