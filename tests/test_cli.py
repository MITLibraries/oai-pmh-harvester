import vcr

from harvester.cli import main


@vcr.use_cassette("tests/fixtures/vcr_cassettes/cli-all-options-except-set-spec.yaml")
def test_harvest_all_options_except_set_spec(caplog, monkeypatch, runner, tmp_path):
    monkeypatch.setenv("SENTRY_DSN", "https://1234567890@00000.ingest.sentry.io/123456")
    with runner.isolated_filesystem(temp_dir=tmp_path):
        filepath = tmp_path / "records.xml"
        result = runner.invoke(
            main,
            [
                "-h",
                "https://dspace.mit.edu/oai/request",
                "-o",
                filepath,
                "-v",
                "harvest",
                "--method",
                "get",
                "-m",
                "oai_dc",
                "-f",
                "2017-12-14",
                "-u",
                "2019-04-05",
                "-sr",
                "oai:dspace.mit.edu:1721.1/115850",
                "--exclude-deleted",
            ],
        )
        assert result.exit_code == 0

        assert "Logger 'root' configured with level=DEBUG" in caplog.text
        assert (
            "Sentry DSN found, exceptions will be sent to Sentry with env=test"
            in caplog.text
        )
        assert (
            "OAI-PMH harvesting from source https://dspace.mit.edu/oai/request with "
            "parameters: method=get, metadata_format=oai_dc, from_date=2017-12-14, "
            "until_date=2019-04-05, set=None, skip_record=('oai:dspace.mit.edu:1721.1/"
            "115850',), exclude_deleted=True" in caplog.text
        )
        assert "Writing records to output file:" in caplog.text
        assert (
            "Skipped retrieving record with identifier "
            "oai:dspace.mit.edu:1721.1/115850 because it is in the skip list"
            in caplog.text
        )
        assert (
            "Harvest completed. Total records harvested (not including deleted "
            "records): 15" in caplog.text
        )


@vcr.use_cassette("tests/fixtures/vcr_cassettes/harvest-from-set.yaml")
def test_harvest_no_options_except_set_spec(caplog, runner, tmp_path):
    with runner.isolated_filesystem(temp_dir=tmp_path):
        filepath = tmp_path / "records.xml"
        result = runner.invoke(
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
        assert "Logger 'root' configured with level=INFO" in caplog.text
        assert "No Sentry DSN found, exceptions will not be sent to Sentry" in caplog.text
        assert (
            "OAI-PMH harvesting from source https://dspace.mit.edu/oai/request with "
            "parameters: method=list, metadata_format=oai_dc, from_date=None, "
            "until_date=None, set=com_1721.1_140587, skip_record=(), "
            "exclude_deleted=False" in caplog.text
        )
        assert "Writing records to output file:" in caplog.text
        assert (
            "Harvest completed. Total records harvested (including deleted "
            "records): 58" in caplog.text
        )


@vcr.use_cassette("tests/fixtures/vcr_cassettes/harvest-get-method-no-records.yaml")
def test_harvest_no_records_get_method(caplog, runner, tmp_path):
    with runner.isolated_filesystem(temp_dir=tmp_path):
        filepath = tmp_path / "records.xml"
        result = runner.invoke(
            main,
            [
                "-h",
                "https://dspace.mit.edu/oai/request",
                "-o",
                filepath,
                "harvest",
                "--method",
                "get",
                "-s",
                "com_1721.1_100263",
            ],
        )
        assert result.exit_code == 0
        assert (
            "No records harvested: the combination of the provided options results in "
            "an empty list." in caplog.text
        )


@vcr.use_cassette("tests/fixtures/vcr_cassettes/harvest-list-method-no-records.yaml")
def test_harvest_no_records_list_method(caplog, runner, tmp_path):
    with runner.isolated_filesystem(temp_dir=tmp_path):
        filepath = tmp_path / "records.xml"
        result = runner.invoke(
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


@vcr.use_cassette("tests/fixtures/vcr_cassettes/harvest-from-set.yaml")
def test_harvest_list_method_and_skip_record_logs_warning(caplog, runner, tmp_path):
    with runner.isolated_filesystem(temp_dir=tmp_path):
        filepath = tmp_path / "records.xml"
    result = runner.invoke(
        main,
        [
            "-h",
            "https://dspace.mit.edu/oai/request",
            "-o",
            filepath,
            "harvest",
            "-s",
            "com_1721.1_140587",
            "-sr",
            "12345",
        ],
    )
    assert result.exit_code == 0
    assert (
        "Option --skip-record only works with the 'get' --method option, these records "
        "will not be skipped during harvest: ('12345',)" in caplog.text
    )


@vcr.use_cassette("tests/fixtures/vcr_cassettes/get-sets.yaml")
def test_setlist(caplog, runner, tmp_path):
    with runner.isolated_filesystem(temp_dir=tmp_path):
        filepath = tmp_path / "sets.json"
        result = runner.invoke(
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
