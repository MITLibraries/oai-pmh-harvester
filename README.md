[![Coverage Status](https://coveralls.io/repos/github/MITLibraries/oai-pmh-harvester/badge.svg?branch=rdi-updates)](https://coveralls.io/github/MITLibraries/oai-pmh-harvester?branch=rdi-updates)

# oai-pmh-harvester

CLI app for harvesting from repositories using OAI-PMH.

## Harvesting

To install and run tests:
- `make install`
- `make test`

To view available commands and main options:
- `pipenv run oai --help`

To run a harvest:
- `pipenv run oai -h [host repo oai-pmh url] -o [path to output file] harvest [any additional desired options]`

## Development

Clone the repo and install the dependencies using [Pipenv](https://docs.pipenv.org/):

```bash
git git@github.com:MITLibraries/oai-pmh-harvester.git
cd oai-pmh-harvester
make install
```

## Docker

To build and run in docker:

```bash
make dist-dev
docker run -it oaiharvester
```

To run this locally in Docker while maintaining the ability to see the output file, you can do something like:

```bash
docker run -it --volume '/FULL/PATH/TO/WHERE/YOU/WANT/FILES/tmp:/app/tmp' oaiharvester -h https://aspace-staff-dev.mit.edu/oai -o tmp/out.xml harvest -m oai_ead
```

## S3 Output

You can save to s3 by passing an s3 url as the --output-file (-o) in a format like:

```bash
-o s3://AWS_KEY:AWS_SECRET_KEY@BUCKET_NAME/FILENAME.xml
```

If you have your credentials stored locally, you can omit the passed params like:

```bash
-o s3://BUCKET_NAME/FILENAME.xml
```

## Required ENV
`SENTRY_DSN` = If set to a valid Sentry DSN, enables Sentry exception monitoring. This is not needed for local development.
`WORKSPACE` = Set to `dev` for local development, this will be set to `stage` and `prod` in those environments by Terraform.