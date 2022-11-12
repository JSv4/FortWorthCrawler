#  Copyright (C) 2022  John Scrudato / Gordium Knot Inc. d/b/a OpenSource.Legal
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.

#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.

#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
from django.contrib.auth import get_user_model

from config import celery_app

User = get_user_model()


@celery_app.task()
def get_document_list_task() -> list[str]:
    """
    Task to crawl the Fort Worth repo API and produce a list of documents... these will then be stored as a daily
    crawl and analyzed to see if any of them have a date modified AFTER what we have for the same doc in our database (
    or are missing from our database entirely). Those will be synced and downloaded. Others will be discarded.

    :return: List of "entryIds" to request document metadata and pdfs for
    """
    return []
