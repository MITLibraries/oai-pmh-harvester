import pytest
import vcr
from sickle import Sickle
from sickle.oaiexceptions import NoRecordsMatch

from harvester.oai import OAIClient, write_records, write_sets


def test_oai_client_init_with_defaults():
    client = OAIClient("https://example.com/oai")
    assert client.source_url == "https://example.com/oai"
    assert type(client.client) == Sickle
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
    assert type(client.client) == Sickle
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
    identifiers = oai_client.get_identifiers()
    assert len(identifiers) == 241
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
    with pytest.raises(NoRecordsMatch):
        oai_client.get_identifiers()


@vcr.use_cassette("tests/fixtures/vcr_cassettes/get-records-include-deleted.yaml")
def test_get_records_include_deleted():
    oai_client = OAIClient(
        "https://dspace.mit.edu/oai/request",
        metadata_format="oai_dc",
        from_date="2017-12-14",
        until_date="2017-12-14",
    )
    identifiers = oai_client.get_identifiers()
    records = oai_client.get_records(identifiers, exclude_deleted=False)
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
    identifiers = oai_client.get_identifiers()
    records = oai_client.get_records(identifiers, exclude_deleted=True)
    assert len(list(records)) == 0


@vcr.use_cassette("tests/fixtures/vcr_cassettes/get-sets.yaml")
def test_get_sets():
    oai_client = OAIClient("https://dspace.mit.edu/oai/request")
    sets = oai_client.get_sets()
    assert {
        "Set name": "Abdul Latif Jameel Poverty Action Lab (J-PAL)",
        "Set spec": "com_1721.1_39118",
    } in sets


@vcr.use_cassette("tests/fixtures/vcr_cassettes/write-records.yaml")
def test_write_records(tmp_path):
    oai_client = OAIClient(
        "https://dspace.mit.edu/oai/request",
        metadata_format="oai_dc",
        from_date="2022-03-01",
        until_date="2022-03-01",
    )
    identifiers = oai_client.get_identifiers()
    records = oai_client.get_records(identifiers, exclude_deleted=True)
    filepath = tmp_path / "records.xml"
    count = write_records(records, filepath)
    with open(filepath) as file:
        contents = file.read()
        assert contents.startswith("<records>\n  <record ")
        assert contents.endswith("</record>\n</records>")
    assert count == 44


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
