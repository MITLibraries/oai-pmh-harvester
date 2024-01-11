[![Coverage Status](https://coveralls.io/repos/github/MITLibraries/oai-pmh-harvester/badge.svg?branch=rdi-updates)](https://coveralls.io/github/MITLibraries/oai-pmh-harvester?branch=rdi-updates)

# oai-pmh-harvester

OAI-PMH-Harvester is a Python CLI application for harvesting metadata from repositories (also known as "Data Providers") available via the Open Archives Initiative Protocol for Metadata Harvesting (OAI-PMH). 

## Development
- To preview a list of available Makefile commands: `make help`
- To install with dev dependencies: `make install`
- To update dependencies: `make update`
- To run unit tests: `make test`
- To lint the repo: `make lint`
- To run the app: `pipenv run oai --help`

### Running the application on your local machine

Create a virtual environment and install dev dependencies: `make install`. 

Additional notes: 

1. To execute the steps below, you can use the following sample url to an OAI-PMH repo: `https://aspace-staff-dev.mit.edu/oai`.

2. To write the output file to an S3 bucket, include S3 in the `-o/--output-file` argument.
   * With AWS credentials: 
      ```
      -o s3://<AWS_KEY>:<AWS_SECRET_KEY>@<BUCKET_NAME>/<output-filename>.xml
      ```
   * Wihout AWS credentials (if you have your credentials stored locally):
      ```
      -o s3://<BUCKET_NAME>/<output-filename>.xml
      ```

#### With Docker

1. Run `make dist-dev` to build the Docker container image.

2. To run a harvest, execute the following command in your terminal:
   ```
   docker run -it --volume <local-file-path>:<docker-file-path>' oai-pmh-harvester-dev -h <url-to-oai-pmh-repo> -o <docker-file-path>/<output-filename>.xml harvest <optional-command-args>
   ```

   **Note:** The `-v/--volume` argument mounts the \<local-file-path> in the current directory into the container at \<docker-file-path>, which allows us to view the generated output file in \<local-file-path>.


#### Without Docker 

1. To run a harvest, execute the following command in your terminal:

   ```
   pipenv run oai -h <url-to-oai-pmh-repo> -o <output-filename>.xml harvest <optional-command-args>
   ```

## Environment variables

### Required

```shell
# Set to dev for local development, this will be set to 'stage' and 'prod' in those environments by Terraform.
WORKSPACE=dev
```

### Optional

```shell
# Required only if a source has records that cause errors during a harvest and --method=get. The value provided must be a space-separated list of OAI-PMH record identifiers to skip during harvest.
RECORD_SKIP_LIST=<oai-pmh-id1> <oai-pmh-id2>

# Sets the interval for logging status updates as records are written to the output file. Defaults to 1000, which will log a status update for every thousandth record.
STATUS_UPDATE_INTERVAL = 1000

# If set to a valid Sentry DSN, enables Sentry exception monitoring This is not needed for local development.
SENTRY_DSN = <sentry-dsn-for-oai-pmh-harvester>
```

## CLI commands

All CLI commands can be run with pipenv run <COMMAND>.

### `oai`

```text
Usage: -c [OPTIONS] COMMAND [ARGS]...

Options:
  -h, --host TEXT         Hostname of server for an OAI-PMH compliant source.
                          [required]
  -o, --output-file TEXT  Filepath for generated output (either an XML file
                          with harvested metadata or a JSON file describing
                          set structure of an OAI-PMH compliant source). This
                          value can be a local filepath or an S3 URI.
                          [required]
  -v, --verbose           Pass to log at debug level instead of info
  --help                  Show this message and exit.

Commands:
  harvest  Harvest command to retrieve records from an OAI-PMH compliant source.
  setlist  Create a JSON file describing the set structure of an OAI-PMH compliant source.
```

### `oai harvest`

```text
Usage: -c harvest [OPTIONS]

  Harvest command to retrieve records from an OAI-PMH compliant source.

Options:
  --method [get|list]         Method for record retrieval. The 'list' method
                              is faster and should be used in most cases;
                              'get' method should be used for ArchivesSpace
                              due to errors retrieving a full record set with
                              the 'list' method.  [default: list]
  -m, --metadata-format TEXT  Alternate metadata format for harvested records.
                              A record should only be returned if the format
                              specified can be disseminated from the item
                              identified by the value of the identifier
                              argument.  [default: oai_dc]
  -f, --from-date TEXT        Filter for files modified on or after this date;
                              format YYYY-MM-DD.
  -u, --until-date TEXT       Filter for files modified before this date;
                              format YYYY-MM-DD.
  -s, --set-spec TEXT         SetSpec of set to be harvested. Limits harvest
                              to records in the provided set.
  -sr, --skip-record TEXT     Set of OAI-PMH identifiers for records to skip
                              during a harvest. Only works when --method=get.
                              Multiple identifiers can be provided using the
                              syntax: '-sr oai:12345 -sr oai:67890'. Values
                              can also be retrieved through the
                              RECORD_SKIP_LIST env var (see README for more
                              details).
  --exclude-deleted           Pass to exclude deleted records from harvest.
  --help                      Show this message and exit.
```

### `oai setlist`
```
Usage: -c setlist [OPTIONS]

  Create a JSON file describing the set structure of an OAI-PMH compliant
  source.

  Uses the OAI-PMH ListSets verbs to retrieve all sets from a repository, and
  writes the set names and specs to a JSON output file.

Options:
  --help  Show this message and exit.
```



