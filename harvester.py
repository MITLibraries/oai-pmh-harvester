#!/usr/bin/env python

from sickle import Sickle
from sickle.iterator import OAIItemIterator
import logging
from datetime import date, timedelta
import click

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

    responses = mysickle.ListRecords(
        **{'metadataPrefix': format,
           # 'set': 'hdl_1721.1_33972'
           'from': from_date
           })

    with open(out, 'wb') as f:
        f.write('<records>'.encode())

        for records in responses:
            f.write(records.raw.encode('utf8'))
            logging.debug(counter)
            counter += 1

        f.write('</records>'.encode())

    logging.info("Total records: %i", counter)

    exit(0)


if __name__ == "__main__":
    harvest()
