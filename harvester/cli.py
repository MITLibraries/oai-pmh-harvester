"""harvester.cli module."""
import json
import logging
import sys

import click
import smart_open
from sickle import Sickle
from sickle.oaiexceptions import NoRecordsMatch

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
    "--output_file",
    required=True,
    help="Filepath to write output to. Can be a local filepath or an S3 URI, e.g. "
    "S3://bucketname/filename.xml.",
)
@click.option("-v", "--verbose", help="Optional: enable debug output.", is_flag=True)
@click.pass_context
def main(ctx, host, output_file, verbose):
    ctx.ensure_object(dict)
    ctx.obj["HOST"] = host
    ctx.obj["OUT"] = output_file
    if verbose:
        logging.basicConfig(
            format="%(asctime)s %(levelname)s %(name)s.%(funcName)s() line %(lineno)d: "
            "%(message)s"
        )
        logger.setLevel(logging.DEBUG)
    else:
        logging.basicConfig(
            format="%(asctime)s %(levelname)s %(name)s.%(funcName)s(): %(message)s"
        )
        logger.setLevel(logging.INFO)


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
@click.pass_context
def harvest(ctx, metadata_format, from_date, until_date, set_spec):
    """Harvest records from an OAI-PMH compliant source and write to an output file."""
    logger.info(
        "OAI-PMH harvesting from source %s with parameters: metadata_format=%s, "
        "from_date=%s, until_date = %s, set=%s",
        ctx.obj["HOST"],
        metadata_format,
        from_date,
        until_date,
        set_spec,
    )

    mysickle = Sickle(ctx.obj["HOST"])
    params = {"metadataPrefix": "oai_dc"}
    if from_date:
        params["from"] = from_date
    if until_date:
        params["until"] = until_date
    if set_spec:
        params["set"] = set_spec
    try:
        responses = mysickle.ListIdentifiers(**params)
    except NoRecordsMatch:
        logger.error(
            "No records harvested: the combination of the provided options results in "
            "an empty list."
        )
        sys.exit()

    identifiers = [record.identifier for record in responses]
    total_records = len(identifiers)
    logger.info("Number of records found to harvest: %d", total_records)

    with smart_open.open(ctx.obj["OUT"], "wb+") as file:
        logger.info("Writing output to file %s", ctx.obj["OUT"])
        file.write("<records>".encode())

        counter_total = 0
        counter_deleted = 0
        counter_active = 0

        for identifier in identifiers:
            counter_total += 1
            logger.debug(
                "Retrieving record %d of %d with identifier=%s",
                counter_total,
                total_records,
                identifier,
            )
            record = mysickle.GetRecord(
                identifier=identifier, metadataPrefix=metadata_format
            )
            logger.debug(
                "Record retrieved:\n  Deleted:%s\n  Header:%s\n  Raw:%s\n",
                record.deleted,
                record.header,
                record.raw,
            )
            if record.deleted is False:
                counter_active += 1
                file.write(record.raw.encode("utf8"))
            else:
                counter_deleted += 1

        file.write("</records>".encode())

    logger.info(
        "Total records harvested: %d\n  Active records: %s\n  Deleted records: %s",
        counter_total,
        counter_active,
        counter_deleted,
    )


@main.command()
@click.pass_context
def setlist(ctx):
    mysickle = Sickle(ctx.obj["HOST"])

    logger.info("Getting set list from %s", ctx.obj["HOST"])
    try:
        responses = mysickle.ListSets()
    except Exception as e:
        logger.error(e)
        sys.exit()

    sets = [{"Set name": set.setName, "Set spec": set.setSpec} for set in responses]
    with open(ctx.obj["OUT"], "w+") as file:
        file.write(json.dumps(sets, indent=2))

    logger.info("Finished harvesting set list, wrote output to file %s", ctx.obj["OUT"])
