# ruff: noqa: FBT001

"""harvester.cli module."""
import logging
import sys
from datetime import timedelta
from time import perf_counter
from typing import Literal

import click
from sickle.oaiexceptions import NoRecordsMatch

from harvester.config import Config
from harvester.oai import OAIClient, write_records, write_sets

logger = logging.getLogger(__name__)

CONFIG = Config()


@click.group()
@click.option(
    "-h",
    "--host",
    required=True,
    help="Hostname of server for an OAI-PMH compliant source.",
)
@click.option(
    "-o",
    "--output-file",
    required=True,
    help="Filepath for generated output (either an XML file with harvested metadata or "
    "a JSON file describing set structure of an OAI-PMH compliant source). "
    "This value can be a local filepath or an S3 URI.",
)
@click.option(
    "-v", "--verbose", help="Pass to log at debug level instead of info", is_flag=True
)
@click.pass_context
def main(ctx: click.Context, host: str, output_file: str, verbose: bool) -> None:
    ctx.ensure_object(dict)
    ctx.obj["START_TIME"] = perf_counter()
    ctx.obj["HOST"] = host
    ctx.obj["OUTPUT_FILE"] = output_file
    logger.info(CONFIG.configure_logger(verbose))
    logger.info(CONFIG.configure_sentry())
    CONFIG.check_required_env_vars()


@main.command()
@click.option(
    "--method",
    default="list",
    show_default=True,
    help="Method for record retrieval. The 'list' method is faster and should "
    "be used in most cases; 'get' method should be used for ArchivesSpace due to "
    "errors retrieving a full record set with the 'list' method.",
    type=click.Choice(["get", "list"], case_sensitive=False),
)
@click.option(
    "-m",
    "--metadata-format",
    default="oai_dc",
    show_default=True,
    help="Alternate metadata format for harvested records. A record should only be "
    "returned if the format specified can be disseminated from the item identified "
    "by the value of the identifier argument.",
)
@click.option(
    "-f",
    "--from-date",
    default=None,
    help="Filter for files modified on or after this date; format YYYY-MM-DD.",
)
@click.option(
    "-u",
    "--until-date",
    default=None,
    help="Filter for files modified before this date; format YYYY-MM-DD.",
)
@click.option(
    "-s",
    "--set-spec",
    default=None,
    show_default=True,
    help="SetSpec of set to be harvested. Limits harvest to records in the "
    "provided set.",
)
@click.option(
    "-sr",
    "--skip-record",
    envvar="RECORD_SKIP_LIST",
    multiple=True,
    show_default=True,
    help="Set of OAI-PMH identifiers for records to skip during a harvest. Only works "
    "when --method=get. Multiple identifiers can be provided using the syntax: "
    "'-sr oai:12345 -sr oai:67890'. Values can also be retrieved through the "
    "RECORD_SKIP_LIST env var (see README for more details).",
)
@click.option(
    "--exclude-deleted",
    help="Pass to exclude deleted records from harvest.",
    is_flag=True,
)
@click.pass_context
def harvest(
    ctx: click.Context,
    method: Literal["get", "list"],
    metadata_format: str,
    from_date: str,
    until_date: str,
    set_spec: str,
    skip_record: tuple[str] | None,
    exclude_deleted: bool,
) -> None:
    """Harvest command to retrieve records from an OAI-PMH compliant source."""
    logger.info(
        "OAI-PMH harvesting from source %s with parameters: method=%s, "
        "metadata_format=%s, from_date=%s, until_date=%s, set=%s, skip_record=%s, "
        "exclude_deleted=%s",
        ctx.obj["HOST"],
        method,
        metadata_format,
        from_date,
        until_date,
        set_spec,
        skip_record,
        exclude_deleted,
    )

    oai_client = OAIClient(
        ctx.obj["HOST"], metadata_format, from_date, until_date, set_spec
    )
    if method == "list" and skip_record:
        logger.warning(
            "Option --skip-record only works with the 'get' --method option, these "
            "records will not be skipped during harvest: %s",
            skip_record,
        )
    try:
        records = oai_client.retrieve_records(
            method, exclude_deleted=exclude_deleted, skip_records=skip_record or None
        )
        logger.info("Writing records to output file: %s", ctx.obj["OUTPUT_FILE"])
        count = write_records(records, ctx.obj["OUTPUT_FILE"])
    except NoRecordsMatch:
        logger.info(
            "No records harvested: the combination of the provided options results in "
            "an empty list."
        )
        sys.exit()

    logger.info(
        "Harvest completed. Total records harvested (%sincluding deleted records): %d",
        "not " if exclude_deleted else "",
        count,
    )
    elapsed_time = perf_counter() - ctx.obj["START_TIME"]
    logger.info(
        "Total time to complete harvest: %s", str(timedelta(seconds=elapsed_time))
    )


@main.command()
@click.pass_context
def setlist(ctx: click.Context) -> None:
    """Create a JSON file describing the set structure of an OAI-PMH compliant source.

    Uses the OAI-PMH ListSets verbs to retrieve all sets from a repository, and writes
    the set names and specs to a JSON output file.
    """
    oai_client = OAIClient(ctx.obj["HOST"])
    logger.info("Getting set list from source: %s", ctx.obj["HOST"])
    sets = oai_client.get_sets()
    logger.info("Writing setlist to output file %s", ctx.obj["OUTPUT_FILE"])
    write_sets(sets, ctx.obj["OUTPUT_FILE"])
    logger.info("Setlist completed")
