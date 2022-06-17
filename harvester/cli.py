"""harvester.cli module."""
import logging
import sys
from datetime import timedelta
from time import perf_counter

import click
from sickle.oaiexceptions import NoRecordsMatch

from harvester.config import configure_logger, configure_sentry
from harvester.oai import OAIClient, write_records, write_sets

logger = logging.getLogger(__name__)


@click.group()
@click.option(
    "-h",
    "--host",
    required=True,
    help="Hostname of OAI-PMH server to harvest from, e.g. "
    "https://dspace.mit.edu/oai/request.",
)
@click.option(
    "-o",
    "--output-file",
    required=True,
    help="Filepath to write output to. Can be a local filepath or an S3 URI, e.g. "
    "S3://bucketname/filename.xml.",
)
@click.option("-v", "--verbose", help="Optional: enable debug output.", is_flag=True)
@click.pass_context
def main(ctx, host, output_file, verbose):
    ctx.ensure_object(dict)
    ctx.obj["START_TIME"] = perf_counter()
    ctx.obj["HOST"] = host
    ctx.obj["OUTPUT_FILE"] = output_file

    root_logger = logging.getLogger()
    logger.info(configure_logger(root_logger, verbose))
    logger.info(configure_sentry())


@main.command()
@click.option(
    "-m",
    "--metadata-format",
    default="oai_dc",
    show_default=True,
    help="Optional: specify alternate metadata format for harvested records (e.g. "
    "mods, mets, oai_dc, qdc, ore).",
)
@click.option(
    "-f",
    "--from-date",
    default=None,
    help="Optional: starting date to harvest records from, in format YYYY-MM-DD. "
    "Limits harvest to records added/updated on or after the provided date.",
)
@click.option(
    "-u",
    "--until-date",
    default=None,
    help="Optional: ending date to harvest records from, in format YYYY-MM-DD. "
    "Limits harvest to records added/updated on or before the provided date.",
)
@click.option(
    "-s",
    "--set-spec",
    default=None,
    show_default=True,
    help="Optional: SetSpec of set to be harvested. Limits harvest to records in the "
    "provided set.",
)
@click.option(
    "--exclude-deleted",
    help="Optional: exclude deleted records from harvest.",
    is_flag=True,
)
@click.pass_context
def harvest(ctx, metadata_format, from_date, until_date, set_spec, exclude_deleted):
    """Harvest records from an OAI-PMH compliant source and write to an output file."""
    logger.info(
        "OAI-PMH harvesting from source %s with parameters: metadata_format=%s, "
        "from_date=%s, until_date=%s, set=%s, exclude_deleted=%s",
        ctx.obj["HOST"],
        metadata_format,
        from_date,
        until_date,
        set_spec,
        exclude_deleted,
    )
    oai_client = OAIClient(
        ctx.obj["HOST"], metadata_format, from_date, until_date, set_spec
    )
    try:
        identifiers = oai_client.get_identifiers()
    except NoRecordsMatch:
        logger.error(
            "No records harvested: the combination of the provided options results in "
            "an empty list."
        )
        sys.exit()
    logger.info(
        "Number of records to harvest (including deleted records): %d",
        len(identifiers),
    )
    records = oai_client.get_records(identifiers, exclude_deleted)
    logger.info("Writing records to output file: %s", ctx.obj["OUTPUT_FILE"])
    count = write_records(records, ctx.obj["OUTPUT_FILE"])
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
def setlist(ctx):
    """Get set info from an OAI-PMH compliant source and write to an output file.

    Uses the OAI-PMH ListSets verbs to retrieve all sets from a repository, and writes
    the set names and specs to a JSON output file.
    """
    oai_client = OAIClient(ctx.obj["HOST"])
    logger.info("Getting set list from source: %s", ctx.obj["HOST"])
    sets = oai_client.get_sets()
    logger.info("Writing setlist to output file %s", ctx.obj["OUTPUT_FILE"])
    write_sets(sets, ctx.obj["OUTPUT_FILE"])
    logger.info("Setlist completed")
