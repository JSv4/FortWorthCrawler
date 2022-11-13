#  Copyright (C) 2022  John Scrudato / Gordium Knot Inc. d/b/a OpenSource.Legal
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
import time
import typing
from typing import TypedDict

#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.

#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry
from rich import json


class TimeoutHTTPAdapter(HTTPAdapter):
    def __init__(self, *args, **kwargs):
        if "timeout" in kwargs:
            self.timeout = kwargs["timeout"]
            del kwargs["timeout"]
        else:
            self.timeout = 5  # or whatever default you want

        super().__init__(*args, **kwargs)

    def send(self, request, **kwargs):
        kwargs["timeout"] = self.timeout
        return super().send(request, **kwargs)


# Some
session = requests.Session()
adapter = TimeoutHTTPAdapter(timeout=(3, 60), max_retries=Retry(total=5, backoff_factor=1.5, allowed_methods=False,
                                                                status_forcelist=[429, 500, 502, 503, 504]))
session.mount("http://", adapter)
session.mount("https://", adapter)

url = """https://publicdocuments.fortworthtexas.gov/CSODOCS/FolderListingService.aspx/GetFolderListing2"""

doc_link_template = r"https://publicdocuments.fortworthtexas.gov/CSODOCS/DocView.aspx?id={{" \
                    r"doc_id}}&dbid=0&repo=City-Secretary"

headers = {
    "Content-Type": "application/json"
}

root_contract_folder_id = 80306
repository = "City-Secretary"

increment = 40
start = 0
end = start + increment


# BASIC API CALLS ######################################################################################################

# TODO - NEED A CALL TO GET DOCUMENT / CONTRACT METADATA

class FieldDataDict(TypedDict):
    name: str
    values: list[str]
    isMvfg: bool


class PageInfoDict(TypedDict):
    pageNum: int
    imageHeight: int
    imageWidth: int
    xdpi: int
    ydpi: int
    rotation: int
    empty: bool
    pageId: int


class DocumentMetadataDict(TypedDict):
    templateName: str
    localizedName: typing.Optional[str]
    modified: str
    created: str
    path: str
    tagIds: list[str]
    fInfo: list[FieldDataDict]
    linkGroup: dict
    documentRelationships: list[typing.Any]
    err: typing.Optional[str]


class DocumentMetadataResponseDict(TypedDict):
    name: str
    id: int
    metadata: DocumentMetadataDict
    iconClass: str
    targetType: int
    pageCount: int
    pageInfos: list[typing.Union[PageInfoDict, None]]
    hasImagedPages: typing.Any  # Don't know what this is supposed to look like... example is just None
    thumbnailPaths: typing.Any  # Don't know what this is supposed to look like... example is just None
    parentId: int
    edocUrl: typing.Any  # Don't know what this is supposed to look like... example is just None
    extension: typing.Any  # Don't know what this is supposed to look like... example is just None
    mediaMimeType: typing.Any  # Don't know what this is supposed to look like... example is just None
    mediaHandleUrl: typing.Any  # Don't know what this is supposed to look like... example is just None
    linkTo: int


def get_document_metadata(entry_id: str, repo_name: str = "City-Secretary") -> DocumentMetadataResponseDict:
    url = r"https://publicdocuments.fortworthtexas.gov/CSODOCS/DocumentService.aspx/GetBasicDocumentInfo"
    request_body = {
        "entryId": entry_id,
        "repoName": repo_name
    }

    # sample_response = {
    #     {
    #         "data": {
    #             "name": "Contract 36651 Volume 1",
    #             "id": 188176,
    #             "metadata": {
    #                 "templateName": "Contracts",
    #                 "localizedName": None,
    #                 "modified": "1/6/2020 3:45:52 PM",
    #                 "created": "1/6/2020 3:45:05 PM",
    #                 "path": "\\0 CS Records Management\\1075-16(a) CONSTRUCTION PROJECT CONTRACTS\\0000-9999\\36651 "
    #                         "Volume 1000-36651 Volume 1999\\Contract 36651 Volume 1",
    #                 "tagIds": [],
    #                 "fInfo": [
    #                     {
    #                         "name": "Contract Number",
    #                         "values": [
    #                             "36651 Volume 1"
    #                         ],
    #                         "isMvfg": False
    #                     },
    #                     {
    #                         "name": "Vendor",
    #                         "values": [
    #                             "S.J. Louis Construction of Texas, Ltd."
    #                         ],
    #                         "isMvfg": False
    #                     },
    #                     {
    #                         "name": "Subject",
    #                         "values": [
    #                             "Contract for the Trinity River Pipeline Crossing at the Village Creek Wastewater "
    #                             "Treatment Plant"
    #                         ],
    #                         "isMvfg": False
    #                     },
    #                     {
    #                         "name": "Approval Date",
    #                         "values": [
    #                             "1/8/2008"
    #                         ],
    #                         "isMvfg": False
    #                     },
    #                     {
    #                         "name": "Construction Contract",
    #                         "values": [
    #                             "Yes"
    #                         ],
    #                         "isMvfg": False
    #                     },
    #                     {
    #                         "name": "M&C Number",
    #                         "values": [
    #                             "C-22616"
    #                         ],
    #                         "isMvfg": False
    #                     },
    #                     {
    #                         "name": "Project Number/ID",
    #                         "values": [
    #                             "00186"
    #                         ],
    #                         "isMvfg": False
    #                     }
    #                 ],
    #                 "linkGroup": {
    #                     "name": None,
    #                     "entries": []
    #                 },
    #                 "documentRelationships": [],
    #                 "err": None
    #             },
    #             "iconClass": "EntryImage Document ",
    #             "targetType": -2,
    #             "pageCount": 576,
    #             "pageInfos": [
    #                 None,
    #                 {
    #                     "pageNum": 1,
    #                     "imageHeight": 3300,
    #                     "imageWidth": 2550,
    #                     "xdpi": 300,
    #                     "ydpi": 300,
    #                     "rotation": 0,
    #                     "empty": False,
    #                     "pageId": 1383043
    #                 },
    #             ],
    #             "hasImagedPages": None,
    #             "thumbnailPaths": None,
    #             "parentId": 188173,
    #             "edocUrl": None,
    #             "extension": None,
    #             "mediaMimeType": None,
    #             "mediaHandlerUrl": None,
    #             "linkTo": 0
    #         }
    #     }
    # }

    metadata_response = session.post(
        url,
        json=request_body
    )
    return metadata_response.json()['data']


class SingleExportStatusDict(TypedDict):
    errMsg: typing.Union[str, bool]
    success: bool
    finished: bool
    completion: int


def get_single_pdf_download_progress(download_token: str) -> SingleExportStatusDict:
    # POST to
    url = r"https://publicdocuments.fortworthtexas.gov/CSODOCS/DocumentService.aspx/PDFTransition"
    print(f"get_single_pdf_download_progress - url: {url}")
    request_body = {
        "Key": download_token
    }

    sample_response = {
        "errMsg": None,
        "success": False,
        "finished": False,
        "completion": 3
    }

    response = session.post(
        url,
        json=request_body
    )

    return response.json()


class BulkExportStatusDict(TypedDict):
    finished: bool
    errorMessage: typing.Union[bool, str]
    token: str
    completion: int
    needAuditReason: bool
    needWatermarkSelection: bool


def get_bulk_pdf_download_progress(token: str) -> BulkExportStatusDict:
    # POST to
    url = r"https://publicdocuments.fortworthtexas.gov/CSODOCS/ZipEntriesHandler.aspx/CheckExportStatus"
    post_body = {
        "token": token
    }

    # response looks like this:
    sample_response = {
        "data": {
            "finished": True,
            "errorMessage": None,
            "token": "72b139fd-aad4-4f26-85da-3e4541b4802b",
            "completion": 100,
            "needAuditReason": False,
            "needWatermarkSelection": False
        }
    }

    # Upon finished = True, you can then download file using a separate GET
    response = session.post(
        url,
        json=post_body
    )
    return response.json()['data']


def request_single_pdf_export(
    entry_id: str,
    start_page: int,
    end_page: int
) -> str:
    # POST to
    url = f"https://publicdocuments.fortworthtexas.gov/CSODOCS/GeneratePDF10.aspx?key={entry_id}&PageRange={start_page}-\
                                                                                                  {end_page}&Watermark=0&repo=City-Secretary"
    # expected response is stupid, basically empty html page that says "ThePDFInitiator10". Some kind of joke for a
    # bored programmer?

    """
    a6dec311-1cb8-4db5-9456-8a7b30ed3754
    <html lang="en-US">

    <body>
            <span id="ThePDFInitiator10"></span>
    </body>
    </html>
    """

    # That first line is the download "Key" you need to get the download when it's ready (and also need to check
    # status of export).
    headers = {
        "Host": "publicdocuments.fortworthtexas.gov",
        "Origin": "https://publicdocuments.fortworthtexas.gov",
        "Refered": f"https://publicdocuments.fortworthtexas.gov/CSODOCS/DocView.aspx?id="
                   f"{entry_id}&dbid=0&repo=City-Secretary",
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:106.0) Gecko/20100101 Firefox/106.0"
    }
    response = session.post(
        url,
        headers=headers
    )

    print(f"Response: {response.content}")
    token = response.content.decode('utf-8').split("\n")[0]
    return token


def request_bulk_pdf_export(entry_ids: list[int]) -> str:
    # POST to
    url = r"https://publicdocuments.fortworthtexas.gov/CSODOCS/ZipEntriesHandler.aspx/StartExport"
    post_body = {
        "ids": entry_ids,
        "key": -1,
        "repoName": "City-Secretary",
        "vdirName": "CSODOCS",
        "watermarkIdx": -1
    }

    # returns a data structure with token you need to monitor progress and initiatve download:
    sample_response = {
        "data": {
            "finished": False,
            "errorMessage": None,
            "token": "31d0687d-f3f7-4e8b-8576-faa0d1145d5a",
            "completion": 0,
            "needAuditReason": False,
            "needWatermarkSelection": False
        }
    }

    # Should return "token" prop
    response = session.post(
        url,
        json=post_body
    )
    return response.json()['data']['token']


def download_bulk_pdfs(
    bulk_download_token: str
):
    # GET to:
    url = f"https://publicdocuments.fortworthtexas.gov/CSODOCS/ExportJobHandler.aspx/GetExportJob/" \
          f"?token={bulk_download_token}"

    response = session.get(url)
    return response.content

    # May need to add "Referer" property to header in form:
    # https://publicdocuments.fortworthtexas.gov/CSODOCS/Browse.aspx?id=265902&dbid=0&repo=City-Secretary

    # Should return ZIP of PDFs in bytes


def download_single_pdf(single_download_key: str, entry_id: str):
    # GET to
    url = f"https://publicdocuments.fortworthtexas.gov/CSODOCS/PDF10/{single_download_key}/{entry_id}"

    # Possibly will need "Referer" header - in this form:
    # https://publicdocuments.fortworthtexas.gov/CSODOCS/DocView.aspx?id=188176&dbid=0&repo=City-Secretary

    # Should return PDF bytes


def request_folder_results(
    repo: str,
    folder_id: int,
    start: int,
    end: int
) -> dict:
    infinite_doc_scroll_payload = {
        "end": end,
        "folderId": folder_id,
        "getNewListing": True,
        "repoName": repo,
        "sortAscending": True,
        "sortColumn": "",
        "start": start
    }

    response = session.post(url, headers=headers, json=infinite_doc_scroll_payload)
    response_obj = response.json()
    response_data = response_obj['data']
    print(f"{repo}/{folder_id} folder content:\n" + json.dumps(response_data, indent=4))
    return response_data


class FolderContentsDict(TypedDict):
    folders: list[dict]
    documents: list[dict]


def get_folder_contents(
    repo: str,
    folder_id: int
) -> FolderContentsDict:
    """
    Uses PaperFiche's undocumented "API" to retrieve the contents of a folder from the Fort
    Worth system.

    :param repo: The folders we're querying exist inside of a parent repo. Not sure what the others other.
    :param folder_id: Folder ID we want to fetch. These are available as part
    :return:
    """

    print(f"\n\nGet folder contents for {repo}/{folder_id}")

    increment = 40
    start = 0
    end = start + increment

    initial_results = request_folder_results(
        repo=repo,
        folder_id=folder_id,
        start=start,
        end=end
    )

    print(f"Raw api response: {initial_results}")

    total_entries = initial_results['totalEntries']
    entries = initial_results['results']

    print(f"Initial results: {entries}")

    doc_results = list(filter(lambda result: result is not None and result['targetType'] == 0 and
                                             result['type'] == -1, entries))
    folder_results = list(filter(lambda result: result is not None and result['targetType'] == 0 and
                                                result['type'] == 0,
                                 entries))
    # I don't fully understand what a "shortcut" is, but I noticed that there is one entryId (188177) that fails when
    # processed as a folder or doc... you get this response when trying to crawl it:
    #
    # {'name': None, 'folderId': 188177, 'colTypes': None, 'results': None, 'failed': True,
    #  'errMsg': 'Mismatched entry type; the actual type is Shortcut. [9001]', 'entryType': 0, 'path': None,
    #  'parentId': 0, 'showColumnPicker': True, 'totalEntries': 0, 'sortAscending': False, 'sortColumn': None}
    #
    # Based on hundreds of examples, it's the only entry (so far) that is has property "type": -1.
    # I think the best way to investigate the right API call is to find this entry in the GUI (title: "Contract 36651
    # Volume 1")

    while end <= total_entries:
        start = start + increment
        end = end + increment

        subsequent_results = request_folder_results(
            repo=repo,
            folder_id=folder_id,
            start=start,
            end=end
        )

        # Looks like maybe this thing has a rate throttle. Slow it down a bit.
        time.sleep(.5)

        print(f"Subsequent results from {start} to {end}: {subsequent_results}")

        doc_results = doc_results + list(filter(lambda result: result is not None and result['targetType'] == 0 and
                                                               result['type'] == -1, subsequent_results['results']))
        folder_results = folder_results + list(
            filter(lambda result: result is not None and result['targetType'] == 0 and
                                  result['type'] == 0, subsequent_results['results']))

        print(f"Doc results: {doc_results}")
        print(f"Folder results: {folder_results}")

    with open("folders.json", "w+") as folders_file:
        for folder in folder_results:
            folders_file.writelines(json.dumps(folder))

    with open("documents.json", "w+") as documents_file:
        for document in doc_results:
            documents_file.writelines(json.dumps(document))

    return {
        "folders": folder_results,
        "documents": doc_results,
    }


# CRAWLER ##############################################################################################################
def crawl_directory_recursively(
    repo: str,
    folder_id: int,
) -> FolderContentsDict:

    # FYI.. the "data" field for a document json has a list of (mostly duplicative values). The 10th and 11th
    # index of that array appear to BOTH be the last modified date of the doc with given entryId, so you do NOT
    # need to request the metadata separately to check if doc has been modified.

    results = get_folder_contents(
        repo=repo,
        folder_id=folder_id
    )

    for subfolder in results['folders']:
        sub_results = crawl_directory_recursively(
            repo=repo,
            folder_id=subfolder['entryId']
        )

        print(f"Subdirectory {folder_id} docs: {sub_results['documents']}")
        print(f"Subdirectory {folder_id} folders: {sub_results['folders']}")

        results['documents'] = [
            *results['documents'],
            *sub_results['documents']
        ]

        results['folders'] = [
            *results['folders'],
            *sub_results['folders']
        ]

    return results


# folder_contents = get_folder_contents(
#     repo="City-Secretary",
#     folder_id=root_contract_folder_id
# )
# print(json.dumps(folder_contents, indent=4))

# full_recursive_results = crawl_directory_recursively(
#     repo="City-Secretary",
#     folder_id=root_contract_folder_id
# );
# with open("crawl_results.json", 'w') as out_file:
#     out_file.write(json.dumps(full_recursive_results))

# with open("crawl_results.json", 'r') as crawl_file:
#     crawl_results = json.loads(crawl_file.read())
#     document_results = crawl_results['documents']
#     print(f"Store document: {document_results[0]}")
#
#     # Test request metadata
#     metadata = get_document_metadata(document_results[0]['entryId'])
#     print(f"Metadata: {metadata}")
#     print(f"Page count: {metadata['pageCount']}")
#
#     # Test single download
#     single_download_start_token = request_single_pdf_export(
#         entry_id=document_results[0]['entryId'],
#         start_page=1,
#         end_page=metadata['pageCount']
#     )
#
#     print(f"Single_download_start_response token: {single_download_start_token}")
#     download_status = get_single_pdf_download_progress(download_token=single_download_start_token)
#     print(f"Download status: {download_status}")
#
#     bulk_download_response = request_bulk_pdf_export(entry_ids=[document_results[0]['entryId']])
#     print(f"Bulk download response: {bulk_download_response}")
#
#     download_status = get_bulk_pdf_download_progress(token=bulk_download_response)
#     bulk_download_finished = download_status['finished']
#
#     while not bulk_download_finished:
#         print(f"Download status: {download_status}")
#         download_status = get_bulk_pdf_download_progress(token=bulk_download_response)
#         bulk_download_finished = download_status['finished']
#         time.sleep(1)
#
#     with open("test.pdf", "wb") as file:
#         file.write(download_bulk_pdfs(bulk_download_token=bulk_download_response))

# response = requests.post(url, headers=headers, json={
#         "end": end,
#         "folderId": root_contract_folder_id,
#         "getNewListing": True,
#         "repoName": "City-Secretary",
#         "sortAscending": True,
#         "sortColumn": "",
#         "start": start
#     })
# print(response.status_code)
# response_obj = response.json()
# response_data = response_obj['data']
#
# totalEntries = response_data['totalEntries']
# print(response_data['totalEntries'])
# print(response_data['path'])
# print(response_data['folderId'])
#
# doc_data = []
# doc_jsons = response_data['results']
# for doc_json in doc_jsons:
#     doc_data.append({
#         "id": doc_json['data'][6],
#         "name": doc_json['data'][0],
#         "page_count": doc_json['data'][1],
#         "type": doc_json['type']
#     })
# print(doc_data)
#
# while end<=totalEntries:
#
#     start+=increment
#     end+=increment
#
#     infinite_doc_scroll_payload = {
#         "end": end+increment,
#         "folderId": 88744,
#         "getNewListing": True,
#         "repoName": "City-Secretary",
#         "sortAscending": True,
#         "sortColumn": "",
#         "start": start+increment
#     }
#
#     response_obj = response.json()
#     response_data = response_obj['data']
#     doc_jsons = response_data['results']
#     for doc_json in doc_jsons:
#         doc_data.append({
#             "id": doc_json['data'][6],
#             "name": doc_json['data'][0],
#             "page_count": doc_json['data'][1],
#             "type": doc_json['type']
#         })
#
# print(doc_data)
