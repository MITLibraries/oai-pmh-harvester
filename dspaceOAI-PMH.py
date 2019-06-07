#!/usr/bin/env python

from sickle import Sickle
from sickle.iterator import OAIResponseIterator
from sickle.iterator import OAIItemIterator
import os
import sys
import io
import argparse
import logging

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
    parser.add_argument('--verbose', help = "show help message and exit")
    parser.add_argument('-host', action='store',  dest='hostname', help='Set hostname', default="https://dspace.mit.edu")
    parser.add_argument('-from', action='store',  dest='from_date', help='Set from date', default="2019-03-01") 
    parser.add_argument('-until', action='store',  dest='until',  help='Until date', default="2019-06-03")   
    parser.add_argument('-metadata-type', action='store',  dest='metadata-type',  help='Add metadata type (e.g. mods, mets, oai_dc, qdc)', default="mods") 
    
    return parser


def get_collection(handle):
    
    logging.debug("Will get collection by handle URL")


def list_collections(handle):
    
    logging.debug("list all available collections")
    

def main():
    
    # uri = URI('https://dspace.mit.edu/oai/request?verb=ListRecords&metadataPrefix=oai_dc')
    
    counter = 0
    
    logging.basicConfig(level=logging.DEBUGop)
    # logging.basicConfig(level=logging.INFO)
    
    args = get_parser().parse_args()
        
    logging.debug("OAI-PMH testing on dspace.mit.edu") 
    logging.debug("From date = %s", args.from_date)   
    
    base_request =  args.hostname + '/oai/request'
      
    # sickle = Sickle('http://dome.mit.edu/oai/request')
    # records = sickle.ListRecords(
        # **{'metadataPrefix': 'mets',
  #       'set': 'hdl_1721.3_45936'
  #       })
        
        
    mysickle = Sickle('https://dspace.mit.edu/oai/request', iterator=OAIItemIterator)
    
    # mysickle = Sickle('https://dspace.mit.edu/oai/request')
        
    # harvesting everything from dspace.mit.edu from the last 3 months
    
    responses = mysickle.ListRecords(
        **{'metadataPrefix': 'mods',
        # 'set': 'hdl_1721.1_33972'
        'from': args.from_date
     })
     
    # with open('/Users/carlj/Developer/Python/oai-pmh/response/dspace.mit.edu_ocw_from-2019-03-01_mods_response.xml', 'wb') as items:
    with open('/Users/carlj/Developer/Python/oai-pmh/dspace.mit.edu_everything_from-2019-03-01_mods_response.xml', 'wb') as items:
        
        for records in responses:
            counter += 1
            if responses.resumption_token:
               items.write(records.raw.encode('utf8'))
               logging.debug(counter)
                 
    logging.debug("Total records: %i", counter)
    logging.debug("Done.")   
    
    exit(0)
if __name__ == "__main__": main()

