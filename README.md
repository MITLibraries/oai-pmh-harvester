# oai-pmh-harvester
Scripts for harvesting from repositories using OAI-PMH

## Harvesting

Do this before proceeding to other commands:
- `pipenv install`
- `pipenv shell`
- `pipenv install --editable .`

To perform a harvest with all default settings:
- `harvest`

To see configuration options:
- `harvest --help`


## Development

Clone the repo and install the dependencies using [Pipenv](https://docs.pipenv.org/):

```bash
$ git git@github.com:MITLibraries/oai-pmh-harvester.git
$ cd oai-pmh-harvester
$ pipenv install --dev
```

## Docker

To build and run in docker:
```
docker build -t harvester .
docker run -it harvester
```

To run this locally in Docker while maintaining the ability to see the output file, you can do something like:
```
docker run -it -v '/FULL/PATH/TO/WHERE/YOU/WANT/FILES/tmp:/app/tmp' harvester --host https://aspace-staff-dev.mit.edu/oai --from_date 2019-09-10 --verbose --out tmp/out.xml --format oai_ead
```
