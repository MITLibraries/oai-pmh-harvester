import pytest
import vcr
from sickle import Sickle
from sickle.oaiexceptions import NoRecordsMatch

from harvester.exceptions import MaxAllowedErrorsReached
from harvester.oai import OAIClient, write_records, write_sets


def test_oai_client_init_with_defaults():
    client = OAIClient("https://example.com/oai")
    assert client.source_url == "https://example.com/oai"
    assert isinstance(client.client, Sickle)
    assert client.metadata_format is None
    assert client.params == {}


def test_oai_client_init_with_args():
    client = OAIClient(
        "https://example.com/oai",
        metadata_format="oai_dc",
        from_date="2022-01-01",
        until_date="2022-01-03",
        set_spec="collection_12",
    )
    assert client.source_url == "https://example.com/oai"
    assert isinstance(client.client, Sickle)
    assert client.metadata_format == "oai_dc"
    assert client.params == {
        "metadataPrefix": "oai_dc",
        "from": "2022-01-01",
        "until": "2022-01-03",
        "set": "collection_12",
    }


@vcr.use_cassette("tests/fixtures/vcr_cassettes/get-identifiers.yaml")
def test_get_identifiers():
    oai_client = OAIClient(
        "https://dspace.mit.edu/oai/request",
        metadata_format="oai_dc",
        from_date="2022-01-01",
        until_date="2022-01-10",
        set_spec="hdl_1721.1_49432",
    )
    identifiers = list(oai_client.get_identifiers(exclude_deleted=False))
    expected_identifiers_count = 171
    assert len(identifiers) == expected_identifiers_count
    assert "oai:dspace.mit.edu:1721.1/137340.2" in identifiers


@vcr.use_cassette("tests/fixtures/vcr_cassettes/get-identifiers-no-matches.yaml")
def test_get_identifiers_no_matches_raises_exception():
    oai_client = OAIClient(
        "https://dspace.mit.edu/oai/request",
        metadata_format="oai_dc",
        from_date="2021-12-26",
        until_date="2021-12-26",
        set_spec="hdl_1721.1_49432",
    )
    identifiers = oai_client.get_identifiers(exclude_deleted=False)
    with pytest.raises(NoRecordsMatch):
        next(identifiers)


@vcr.use_cassette("tests/fixtures/vcr_cassettes/get-records-include-deleted.yaml")
def test_get_records_include_deleted():
    oai_client = OAIClient(
        "https://dspace.mit.edu/oai/request",
        metadata_format="oai_dc",
        from_date="2017-12-14",
        until_date="2017-12-14",
    )
    identifiers = oai_client.get_identifiers(exclude_deleted=False)
    records = oai_client.get_records(identifiers)
    for record in records:
        assert (
            '<header status="deleted"><identifier>oai:dspace.mit.edu:1721.1/112746'
            "</identifier>" in record.raw
        )


@vcr.use_cassette("tests/fixtures/vcr_cassettes/get-records-exclude-deleted.yaml")
def test_get_records_exclude_deleted():
    oai_client = OAIClient(
        "https://dspace.mit.edu/oai/request",
        metadata_format="oai_dc",
        from_date="2017-12-14",
        until_date="2017-12-14",
    )
    identifiers = oai_client.get_identifiers(exclude_deleted=True)
    records = oai_client.get_records(identifiers)
    assert len(list(records)) == 0


@vcr.use_cassette("tests/fixtures/vcr_cassettes/record-not-found.yaml")
def test_get_records_id_not_found_logs_warning(caplog):
    oai_client = OAIClient(
        "https://dspace.mit.edu/oai/request",
        metadata_format="oai_dc",
        from_date="2021-11-09T03:30:00Z",
        until_date="2021-11-09T04:00:00Z",
    )
    identifiers = oai_client.get_identifiers(exclude_deleted=False)
    records = oai_client.get_records(identifiers)
    list(records)
    assert (
        "Identifier oai:dspace.mit.edu:1721.1/137785 retrieved in identifiers list "
        "returned 'id does not exist' during getRecord request" in caplog.text
    )


@vcr.use_cassette("tests/fixtures/vcr_cassettes/get-records-include-deleted.yaml")
def test_get_records_id_in_skip_list_skips_record():
    skips = ["oai:dspace.mit.edu:1721.1/112746", "a-different-id"]
    oai_client = OAIClient(
        "https://dspace.mit.edu/oai/request",
        metadata_format="oai_dc",
        from_date="2017-12-14",
        until_date="2017-12-14",
    )
    identifiers = oai_client.get_identifiers(exclude_deleted=False)
    records = oai_client.get_records(identifiers, skip_list=skips)
    assert len(list(records)) == 0


@vcr.use_cassette("tests/fixtures/vcr_cassettes/list-records-include-deleted.yaml")
def test_list_records_include_deleted():
    oai_client = OAIClient(
        "https://dspace.mit.edu/oai/request",
        metadata_format="oai_dc",
        from_date="2017-12-14",
        until_date="2017-12-14",
    )
    records = oai_client.list_records(exclude_deleted=False)
    for record in records:
        assert (
            '<header status="deleted"><identifier>oai:dspace.mit.edu:1721.1/112746'
            "</identifier>" in record.raw
        )


@vcr.use_cassette("tests/fixtures/vcr_cassettes/list-records-exclude-deleted.yaml")
def test_list_records_exclude_deleted():
    oai_client = OAIClient(
        "https://dspace.mit.edu/oai/request",
        metadata_format="oai_dc",
        from_date="2017-12-14",
        until_date="2017-12-14",
    )
    records = oai_client.list_records(exclude_deleted=True)
    assert len(list(records)) == 0


@vcr.use_cassette("tests/fixtures/vcr_cassettes/get-sets.yaml")
def test_get_sets():
    oai_client = OAIClient("https://dspace.mit.edu/oai/request")
    sets = oai_client.get_sets()
    assert {
        "Set name": "Abdul Latif Jameel Poverty Action Lab (J-PAL)",
        "Set spec": "com_1721.1_39118",
    } in sets


@vcr.use_cassette("tests/fixtures/vcr_cassettes/get-records-include-deleted.yaml")
def test_retrieve_records_get_method():
    oai_client = OAIClient(
        "https://dspace.mit.edu/oai/request",
        metadata_format="oai_dc",
        from_date="2017-12-14",
        until_date="2017-12-14",
    )
    records = oai_client.retrieve_records(method="get", exclude_deleted=False)
    assert len(list(records)) == 1


@vcr.use_cassette("tests/fixtures/vcr_cassettes/list-records-include-deleted.yaml")
def test_retrieve_records_list_method():
    oai_client = OAIClient(
        "https://dspace.mit.edu/oai/request",
        metadata_format="oai_dc",
        from_date="2017-12-14",
        until_date="2017-12-14",
    )
    records = oai_client.retrieve_records(method="list", exclude_deleted=False)
    assert len(list(records)) == 1


def test_retrieve_records_wrong_method_raises_error():
    oai_client = OAIClient("https://dspace.mit.edu/oai/request")
    with pytest.raises(
        ValueError,
        match='Method must be either "get" or "list", method provided was "wrong"',
    ):
        oai_client.retrieve_records(method="wrong", exclude_deleted=False)


@vcr.use_cassette("tests/fixtures/vcr_cassettes/write-records.yaml")
def test_write_records(caplog, monkeypatch, tmp_path):
    monkeypatch.setenv("STATUS_UPDATE_INTERVAL", "10")
    oai_client = OAIClient(
        "https://dspace.mit.edu/oai/request",
        metadata_format="oai_dc",
        from_date="2022-03-01",
        until_date="2022-03-01",
    )
    records = oai_client.retrieve_records(method="get", exclude_deleted=True)
    filepath = tmp_path / "records.xml"
    count = write_records(records, filepath)
    with open(filepath) as file:
        contents = file.read()
        assert contents.startswith(
            '<?xml version="1.0" encoding="UTF-8"?>\n<records>\n  <record '
        )
        assert contents.endswith("</record>\n</records>")
    expected_records_count = 32
    assert count == expected_records_count
    assert "Status update: 30 records written to output file so far!" in caplog.text


def test_write_sets(tmp_path):
    sets = [{"Set name": "A majestic collection", "Set spec": "12345"}]
    filepath = tmp_path / "sets.json"
    write_sets(sets, filepath)
    with open(filepath) as file:
        contents = file.read()
        assert contents == (
            '[\n  {\n    "Set name": "A majestic collection",\n    '
            '"Set spec": "12345"\n  }\n]'
        )


@vcr.use_cassette("tests/fixtures/vcr_cassettes/get-records-two-errors.yaml")
def test_complete_harvest_with_skipped_errors_and_report(mock_sentry_capture_message):
    oai_client = OAIClient(
        "https://dspace.mit.edu/oai/request",
        metadata_format="oai_dc",
        retry_status_codes=(),  # skip retrying any HTTP codes
    )
    identifiers = [
        "oai:dspace.mit.edu:1721.1/152958",
        "oai:dspace.mit.edu:1721.1/152786",  # threw 500 error at time of recording
        "oai:dspace.mit.edu:1721.1/147573",  # threw 500 error at time of recording
        "oai:dspace.mit.edu:1721.1/152939",
    ]
    records = list(oai_client.get_records(identifier for identifier in identifiers))
    expected_records_count = 2
    assert len(records) == expected_records_count
    assert mock_sentry_capture_message.called


@vcr.use_cassette("tests/fixtures/vcr_cassettes/get-records-two-errors.yaml")
def test_aborted_harvest_with_max_errors_reached_and_report(
    mock_sentry_capture_message,
):
    oai_client = OAIClient(
        "https://dspace.mit.edu/oai/request",
        metadata_format="oai_dc",
        retry_status_codes=(),
    )
    identifiers = [
        "oai:dspace.mit.edu:1721.1/152958",
        "oai:dspace.mit.edu:1721.1/152786",  # threw 500 error at time of recording
        "oai:dspace.mit.edu:1721.1/147573",  # threw 500 error at time of recording
        "oai:dspace.mit.edu:1721.1/152939",
    ]
    with pytest.raises(MaxAllowedErrorsReached):
        _ = list(
            oai_client.get_records(
                (identifier for identifier in identifiers),
                max_allowed_errors=1,  # set max errors to 1
            )
        )
    assert mock_sentry_capture_message.called
