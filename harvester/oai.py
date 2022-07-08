"""oai.py module."""
import json
import logging
import os
from typing import Iterator, Literal, Optional

import smart_open
from sickle import Sickle
from sickle.models import Record
from sickle.oaiexceptions import IdDoesNotExist

from harvester.config import DEFAULT_RETRY_AFTER, MAX_RETRIES, RETRY_STATUS_CODES

logger = logging.getLogger(__name__)


class OAIClient:
    def __init__(
        self,
        source_url: str,
        metadata_format: Optional[str] = None,
        from_date: Optional[str] = None,
        until_date: Optional[str] = None,
        set_spec: Optional[str] = None,
    ) -> None:
        self.source_url = source_url
        self.client = Sickle(
            self.source_url,
            default_retry_after=DEFAULT_RETRY_AFTER,
            max_retries=MAX_RETRIES,
            retry_status_codes=RETRY_STATUS_CODES,
        )
        self.metadata_format = metadata_format
        self._set_params(metadata_format, from_date, until_date, set_spec)

    def _set_params(
        self,
        metadata_format: Optional[str],
        from_date: Optional[str],
        until_date: Optional[str],
        set_spec: Optional[str],
    ) -> None:
        params = {}
        if metadata_format:
            params["metadataPrefix"] = metadata_format
        if from_date:
            params["from"] = from_date
        if until_date:
            params["until"] = until_date
        if set_spec:
            params["set"] = set_spec
        self.params = params

    def get_identifiers(self, exclude_deleted: bool) -> Iterator[str]:
        responses = self.client.ListIdentifiers(
            ignore_deleted=exclude_deleted, **self.params
        )
        for record in responses:
            yield record.identifier

    def get_records(self, identifiers: Iterator[str]) -> Iterator[Record]:
        for identifier in identifiers:
            try:
                record = self.client.GetRecord(
                    identifier=identifier, metadataPrefix=self.metadata_format
                )
                logger.debug("Record retrieved: %s", identifier)
            except IdDoesNotExist:
                logger.warning(
                    "Identifier %s retrieved in identifiers list returned 'id does not "
                    "exist' during getRecord request",
                    identifier,
                )
            yield record

    def get_sets(self):
        responses = self.client.ListSets()
        sets = [{"Set name": set.setName, "Set spec": set.setSpec} for set in responses]
        return sets

    def list_records(self, exclude_deleted: bool) -> Iterator[Record]:
        return self.client.ListRecords(ignore_deleted=exclude_deleted, **self.params)

    def retrieve_records(
        self, method: Literal["get", "list"], exclude_deleted: bool
    ) -> Iterator[Record]:
        if method == "get":
            identifiers = self.get_identifiers(exclude_deleted)
            return self.get_records(identifiers)
        elif method == "list":
            return self.list_records(exclude_deleted)
        else:
            raise ValueError(
                'Method must be either "get" or "list", method provided was "{method}"'
            )


def write_records(records: Iterator, filepath: str) -> int:
    count = 0
    with smart_open.open(filepath, "wb") as file:
        file.write('<?xml version="1.0" encoding="UTF-8"?>\n<records>\n'.encode())
        for record in records:
            file.write("  ".encode() + record.raw.encode() + "\n".encode())
            count += 1
            if count % int(os.getenv("STATUS_UPDATE_INTERVAL", "1000")) == 0:
                logger.info(
                    "Status update: %s records written to output file so far!",
                    count,
                )
        file.write("</records>".encode())
    return count


def write_sets(sets: list[dict[str, str]], filepath: str) -> None:
    with open(filepath, "w") as file:
        file.write(json.dumps(sets, indent=2))
