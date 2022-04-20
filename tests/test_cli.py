import logging

import vcr

from harvester.cli import main


@vcr.use_cassette("tests/fixtures/vcr_cassettes/get-records-exclude-deleted.yaml")
def test_harvest_all_options_except_set_spec(caplog, cli_runner, tmp_path):
    caplog.set_level(logging.DEBUG)
    with cli_runner.isolated_filesystem(temp_dir=tmp_path):
        filepath = tmp_path / "records.xml"
        result = cli_runner.invoke(
            main,
            [
                "-h",
                "https://dspace.mit.edu/oai/request",
                "-o",
                filepath,
                "-v",
                "harvest",
                "-m",
                "oai_dc",
                "-f",
                "2017-12-14",
                "-u",
                "2017-12-14",
                "--exclude-deleted",
            ],
        )
        assert result.exit_code == 0
        assert (
            "OAI-PMH harvesting from source https://dspace.mit.edu/oai/request with "
            "parameters: metadata_format=oai_dc, from_date=2017-12-14, until_date="
            "2017-12-14, set=None, exclude_deleted=True" in caplog.text
        )
        assert (
            "Number of records to harvest (including deleted records): 1" in caplog.text
        )
        assert "Writing records to output file:" in caplog.text
        assert (
            "Record retrieved:\n  Deleted:True\n  Header:"
            '<header xmlns="http://www.openarchives.org/OAI/2.0/" ' in caplog.text
        )
        assert (
            "Harvest completed. Total records harvested (not including deleted "
            "records): 0" in caplog.text
        )


@vcr.use_cassette("tests/fixtures/vcr_cassettes/harvest-from-set.yaml")
def test_harvest_no_options_except_set_spec(caplog, cli_runner, tmp_path):
    caplog.set_level(logging.INFO)
    with cli_runner.isolated_filesystem(temp_dir=tmp_path):
        filepath = tmp_path / "records.xml"
        result = cli_runner.invoke(
            main,
            [
                "-h",
                "https://dspace.mit.edu/oai/request",
                "-o",
                filepath,
                "harvest",
                "-s",
                "com_1721.1_140587",
            ],
        )
        assert result.exit_code == 0
        assert (
            "OAI-PMH harvesting from source https://dspace.mit.edu/oai/request with "
            "parameters: metadata_format=oai_dc, from_date=None, until_date="
            "None, set=com_1721.1_140587, exclude_deleted=False" in caplog.text
        )
        assert (
            "Number of records to harvest (including deleted records): 58"
            in caplog.text
        )
        assert "Writing records to output file:" in caplog.text
        assert (
            "Harvest completed. Total records harvested (including deleted "
            "records): 58" in caplog.text
        )


@vcr.use_cassette("tests/fixtures/vcr_cassettes/harvest-no-records.yaml")
def test_harvest_no_records(caplog, cli_runner, tmp_path):
    with cli_runner.isolated_filesystem(temp_dir=tmp_path):
        filepath = tmp_path / "records.xml"
        result = cli_runner.invoke(
            main,
            [
                "-h",
                "https://dspace.mit.edu/oai/request",
                "-o",
                filepath,
                "harvest",
                "-s",
                "com_1721.1_100263",
            ],
        )
        assert result.exit_code == 0
        assert (
            "No records harvested: the combination of the provided options results in "
            "an empty list." in caplog.text
        )


@vcr.use_cassette("tests/fixtures/vcr_cassettes/get-sets.yaml")
def test_setlist(caplog, cli_runner, tmp_path):
    with cli_runner.isolated_filesystem(temp_dir=tmp_path):
        filepath = tmp_path / "sets.json"
        result = cli_runner.invoke(
            main,
            [
                "-h",
                "https://dspace.mit.edu/oai/request",
                "-o",
                filepath,
                "setlist",
            ],
        )
        assert result.exit_code == 0
        assert (
            "Getting set list from source: https://dspace.mit.edu/oai/request"
            in caplog.text
        )
        assert "Writing setlist to output file " in caplog.text
        assert "Setlist completed" in caplog.text
