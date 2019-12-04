#!/usr/bin/env python

from datetime import date, timedelta
import logging
import sys

import click
from sickle import Sickle
from sickle.iterator import OAIItemIterator
from sickle.oaiexceptions import NoRecordsMatch
from smart_open import open

yesterday = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
tomorrow = (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')


@click.command()
@click.option('--host',
              default="https://dspace.mit.edu/oai/request",
              help='hostname of OAI-PMH server to harvest from')
@click.option('--from_date',
              default=yesterday,
              help='from date format: YYYY-MM-DD')
@click.option('--until',
              default=tomorrow,
              help='until date format: YYYY-MM-DD')
@click.option('--format',
              default='oai_dc',
              help='Add metadata type (e.g. mods, mets, oai_dc, qdc)')
@click.option('--out', default='out.xml', help='Filepath to write output')
@click.option('--verbose', help='Enable debug output', is_flag=True)
def harvest(host, from_date, until, format, out, verbose):
    counter = 0

    if verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    logging.info("OAI-PMH harvesting from %s", host)
    logging.info("From date = %s", from_date)
    logging.info("Until date = %s", until)
    logging.info("Metadata format = %s", format)
    logging.info("Outfile = %s", out)

    mysickle = Sickle(host, iterator=OAIItemIterator)

    try:
        responses = mysickle.ListIdentifiers(
            **{'metadataPrefix': format,
               # 'set': 'hdl_1721.1_33972'
               'from': from_date,
               'until': until
               })
    except NoRecordsMatch:
        logging.info("No records harvested: the combination of the values of "
                     "the arguments results in an empty list.")
        sys.exit()

    identifier_list = []

    for records in responses:
        identifier_list.append(records.identifier)

    logging.info(f"Identifier count to harvest: {len(identifier_list)}")

    with open(out, 'wb') as f:
        f.write('<records>'.encode())

        for identifier in identifier_list:
            r = mysickle.GetRecord(identifier=identifier,
                                   metadataPrefix=format)
            f.write(r.raw.encode('utf8'))
            logging.debug(counter)
            logging.debug(r.raw)
            counter += 1

        f.write('</records>'.encode())

    logging.info("Total records harvested: %i", counter)


if __name__ == "__main__":
    harvest()
