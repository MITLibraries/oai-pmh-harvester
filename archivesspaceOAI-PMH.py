from sickle import Sickle

sickle = Sickle('https://emmas-lib.mit.edu/oai/')

counter = 0
date = '1900-01-01'
with open('response.xml', 'wb') as f:
    f.write('<records>'.encode())
    records = sickle.ListRecords(**{'metadataPrefix': 'oai_mods', 'from': date,
                                 'set': 'collection', 'ignore_deleted': True})
    for record in records:
        counter += 1
        print(counter)
        f.write(record.raw.encode('utf8'))
    f.write('</records>'.encode())
