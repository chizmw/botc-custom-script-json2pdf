"""A small helper for parsing multipart/form-data requests."""
import json
import os
import re
from typing import Any
from requests_toolbelt.multipart import decoder  # type: ignore


class MultipartDecoder:
    """A small helper for parsing multipart/form-data requests."""

    def __init__(self, multipart_data) -> None:
        """Initialise the MultipartDecoder.

        Args:
            multipart_data_string (bytes): The raw multipart/form-data string
            received in the event
        """

        # convert the multipart data to a string if it's not already
        if isinstance(multipart_data, bytes):
            # convert the multipart data to a string
            self.multipart_data_str = multipart_data.decode()
        elif isinstance(multipart_data, str):
            self.multipart_data_str = multipart_data
        else:
            # throw an error if we get something we don't understand
            raise TypeError(
                f"multipart_data must be a string or bytes, not {type(multipart_data)}"
            )

        # The boundary is always the first line of the request body.
        self.boundary: str = self.multipart_data_str.split("\r\n")[0]
        # we remove TWO of the dashes from the boundary.
        self.boundary = self.boundary[2:]

        self.content_type: str = f"multipart/form-data; boundary={self.boundary}"

        self.decoded = self._decode().parts

        # set an empty and sad default
        self.form_data: dict[str, Any] = {"files": {}, "fields": {}}
        # and then fill it with the data from the request
        self._process_parts()

        if os.environ.get("BOTC_DEBUG"):
            print(json.dumps(self.form_data, default=str))

    def _decode(self) -> decoder.MultipartDecoder:
        # we need to send bytes to the decoder, so we encode the string
        return decoder.MultipartDecoder(
            self.multipart_data_str.encode("utf-8"), self.content_type
        )

    def _process_parts(self) -> None:
        for part in self.decoded:
            # a bit icky, but I had so many problems with the various modules
            # on offer this ended up being the best solution
            content_disposition_header = part.headers[b"Content-Disposition"].decode()
            header_items = re.findall(r'(\w+)="([^"]*)"', content_disposition_header)
            header_dict = dict(header_items)

            if "filename" in header_dict:
                file_name = header_dict["filename"]
                content_type = part.headers[b"Content-Type"].decode()
                file_content = part.content

                self.form_data["files"][file_name] = {
                    "name": file_name,
                    "content_type": content_type,
                    "content": file_content,
                }

                # if the file is a json file, we can parse it
                if content_type == "application/json":
                    self.form_data["files"][file_name]["json"] = json.loads(
                        file_content
                    )
            else:
                field_name = header_dict["name"]
                field_value = part.text

                self.form_data["fields"][field_name] = field_value

    # a method to get a file by name
    def get_file(self, file_name: str) -> dict[str, Any]:
        """Get a file by name.

        Args:
            file_name (str): the name of the file to get

        Returns:
            dict[str, Any]: the file data
        """
        return self.form_data["files"][file_name]

    # a method to get a field by name
    def get_field(self, field_name: str) -> Any:
        """Get a field by name.

        Args:
            field_name (str): the name of the field to get

        Returns:
            Any: the field data
        """
        return self.form_data["fields"][field_name]

    # get the names of all the files
    def get_file_names(self) -> list[str]:
        """Get the names of all the files.

        Returns:
            list[str]: a list of file names
        """

        # do not do this - you get dist_keys, not a list
        # return self.form_data["files"].keys()

        # do this instead
        return list(self.form_data["files"].keys())
