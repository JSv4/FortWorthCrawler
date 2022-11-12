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

def calc_pdf_file_path(instance, filename, sub_folder):
    return f"documents/{sub_folder}/{convert_api_repo_path_to_file_path(instance.repository_folder_path)}/{filename}"


def convert_api_repo_path_to_file_path(path):

    """
    # Paths in fort worth repo are like this

    "\\0 CS Records Management\\1075-16(a) CONSTRUCTION PROJECT CONTRACTS\\0000-9999\\36651 Volume 1000-36651 Volume 1999\\Contract 36651 Volume 1"

    Basically need to replace "\\" with linux path separator to create a path for django storages

    :param path: Doc path from Fort Worth laserfiche system which has \\ as separator.
    :return: Proper linux path which can be used in S3 or local system
    """

    return "/".join(path.split("\\"))[1:]

