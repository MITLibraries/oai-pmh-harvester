#!/usr/bin/env python

from sickle import Sickle
from sickle.iterator import OAIResponseIterator
from sickle.iterator import OAIItemIterator
import os
import sys
import io
import argparse
import logging
from datetime import date, timedelta

#  sample test community URL's
#  test community (Abdul Latif Jameel Poverty Action Lab):  http://dspace.mit.edu/handle/1721.1/39118
# CSAIL  - http://dspace.mit.edu/handle/1721.1/5458

#  https://dspace.mit.edu/oai/request?verb=ListRecords&metadataPrefix=oai_dc

# resumption token looks like: <resumptionToken expirationDate="2015-06-24T22:38:19Z">0001-01-01T00:00:00Z/9999-12-31T23:59:59Z//oai_dc/100</resumptionToken>
#  sickle tutorials:  https://stackoverflow.com/questions/27680177/getting-all-records-in-a-set-using-the-sickle-package

#  Earth Resources Laboratory:  https://dspace.mit.edu/handle/1721.1/67704

#  command line options from, until date format: YYYY-MM-DD
#  TODO: add metadata types:   mods, qdc, oai_dc, mets, other?
def get_parser():
    # Get parser object
    # from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
    parser = argparse.ArgumentParser()

    parser.add_argument('-host', action='store',  dest='host', help='Set hostname', default="https://dspace.mit.edu/oai/request")

    yesterday = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
    parser.add_argument('-from', action='store',  dest='from_date', help='Set from date, ex: 2019-03-01', default=yesterday)

    tomorrow = (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')
    parser.add_argument('-until', action='store',  dest='until',  help='Until date, ex: 2019-03-01', default=tomorrow)

    parser.add_argument('-format', action='store',  dest='format',  help='Add metadata type (e.g. mods, mets, oai_dc, qdc)', default="oai_dc")

    parser.add_argument('-out', action='store',  dest='out',  help='Filepath to write output, default is current directory out.xml', default="out.xml")

    return parser


def main():
    counter = 0

    logging.basicConfig(level=logging.DEBUG)

    args = get_parser().parse_args()

    logging.debug("OAI-PMH harvesting from %s", args.host)
    logging.debug("From date = %s", args.from_date)

    mysickle = Sickle(args.host, iterator=OAIItemIterator)

    responses = mysickle.ListRecords(
        **{'metadataPrefix': args.format,
        # 'set': 'hdl_1721.1_33972'
        'from': args.from_date
     })

    with open(args.out, 'wb') as f:
        f.write('<records>'.encode())

        for records in responses:
            f.write(records.raw.encode('utf8'))
            logging.debug(counter)
            counter += 1

        f.write('</records>'.encode())

    logging.debug("Total records: %i", counter)
    logging.debug("Done.")

    exit(0)


if __name__ == "__main__": main()
