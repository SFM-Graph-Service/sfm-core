"""
Tests for the SDMX 2.1 adapter.

Covers agency resolution, URL building, SDMX-JSON (series-keyed, flat, v2
wrapper, attributes), SDMX-ML (Generic and StructureSpecific), local files,
detection, mapping to SocialFabricIndicator, and error handling.
"""

import json
from unittest.mock import Mock, patch

import pytest

from data.importers import ImportConfig, SDMXAdapter, SDMX_AGENCIES, MappingTemplates
from data.importers.validators import ValidationError


SERIES_JSON = {
    "structure": {
        "dimensions": {
            "dataSet": [],
            "series": [
                {"id": "FREQ", "values": [{"id": "M", "name": "Monthly"}]},
                {"id": "CURRENCY", "values": [{"id": "USD", "name": "US dollar"}]},
                {"id": "REF_AREA", "values": [{"id": "U2", "name": "Euro area"}]},
            ],
            "observation": [
                {"id": "TIME_PERIOD", "values": [{"id": "2024-01"}, {"id": "2024-02"}]},
            ],
        },
        "attributes": {
            "series": [{"id": "UNIT_MEASURE", "values": [{"id": "USD"}]}],
            "observation": [{"id": "OBS_STATUS", "values": [{"id": "A", "name": "Normal"}]}],
        },
    },
    "dataSets": [{
        "series": {
            "0:0:0": {
                "attributes": [0],
                "observations": {"0": [1.09, 0], "1": [1.08, None]},
            }
        }
    }],
}

FLAT_JSON_V2 = {
    "data": {
        "structures": [{
            "dimensions": {
                "observation": [
                    {"id": "GEO", "values": [{"id": "DE"}, {"id": "FR"}]},
                    {"id": "TIME_PERIOD", "values": [{"id": "2022"}]},
                ]
            }
        }],
        "dataSets": [{"observations": {"0:0": [4000.5], "1:0": [None], "2:0": [1.0]}}],
    }
}

GENERIC_XML = """<?xml version="1.0"?>
<message:GenericData xmlns:message="http://www.sdmx.org/resources/sdmxml/schemas/v2_1/message"
                     xmlns:generic="http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic">
  <message:DataSet>
    <generic:Series>
      <generic:SeriesKey>
        <generic:Value id="FREQ" value="A"/>
        <generic:Value id="REF_AREA" value="US"/>
      </generic:SeriesKey>
      <generic:Attributes><generic:Value id="UNIT_MEASURE" value="PC"/></generic:Attributes>
      <generic:Obs>
        <generic:ObsDimension value="2021"/>
        <generic:ObsValue value="5.5"/>
        <generic:Attributes><generic:Value id="OBS_STATUS" value="A"/></generic:Attributes>
      </generic:Obs>
      <generic:Obs>
        <generic:ObsDimension value="2022"/>
        <generic:ObsValue value="NaN"/>
      </generic:Obs>
    </generic:Series>
  </message:DataSet>
</message:GenericData>"""

STRUCTURE_SPECIFIC_XML = """<?xml version="1.0"?>
<message:StructureSpecificData xmlns:message="http://www.sdmx.org/resources/sdmxml/schemas/v2_1/message">
  <message:DataSet>
    <Series FREQ="Q" REF_AREA="JP" UNIT_MEASURE="JPY">
      <Obs TIME_PERIOD="2023-Q1" OBS_VALUE="100.25"/>
      <Obs TIME_PERIOD="2023-Q2" OBS_VALUE="101"/>
    </Series>
    <Obs FREQ="A" REF_AREA="CA" TIME_PERIOD="2023" OBS_VALUE="7"/>
  </message:DataSet>
</message:StructureSpecificData>"""


class TestAgencyResolution:
    def test_known_codes(self):
        adapter = SDMXAdapter(agency="ecb", flow="EXR", key="M.USD.EUR.SP00.A")
        assert adapter.agency == "ECB"
        assert adapter.base_url == SDMX_AGENCIES["ECB"]
        assert adapter.build_url() == "https://data-api.ecb.europa.eu/service/data/EXR/M.USD.EUR.SP00.A"

    def test_full_base_url(self):
        adapter = SDMXAdapter(agency="https://stats.example.org/sdmx/", flow="F")
        assert adapter.agency == "stats.example.org"
        assert adapter.build_url() == "https://stats.example.org/sdmx/data/F/all"

    def test_unknown_agency_raises(self):
        with pytest.raises(ValueError) as excinfo:
            SDMXAdapter(agency="NOPE", flow="F")
        assert "Unknown SDMX agency" in str(excinfo.value)
        with pytest.raises(ValueError):
            SDMXAdapter(agency="", flow="F")

    def test_source_string_overrides_constructor(self):
        adapter = SDMXAdapter(agency="ECB", flow="X")
        with patch("data.importers.sdmx_adapter.requests.get") as mock_get:
            mock_get.return_value = Mock(text=json.dumps(FLAT_JSON_V2), raise_for_status=Mock())
            list(adapter.extract_nodes("sdmx:EUROSTAT:nama_10_gdp:A.CP_MEUR.B1GQ.DE"))
        assert adapter.agency == "EUROSTAT"
        assert adapter.flow == "nama_10_gdp"
        assert adapter.key == "A.CP_MEUR.B1GQ.DE"
        url = mock_get.call_args[0][0]
        assert url == SDMX_AGENCIES["EUROSTAT"] + "/data/nama_10_gdp/A.CP_MEUR.B1GQ.DE"


class TestDetection:
    def test_detects_prefix_dict_and_files(self, tmp_path):
        adapter = SDMXAdapter(agency="ECB", flow="EXR")
        assert adapter.detect_format("sdmx:ECB:EXR") is True
        assert adapter.detect_format(SERIES_JSON) is True
        assert adapter.detect_format({"flow": "EXR"}) is True
        assert adapter.detect_format("oecd:QNA") is False
        assert adapter.detect_format("data.csv") is False

        xml_file = tmp_path / "d.xml"
        xml_file.write_text(GENERIC_XML)
        assert adapter.detect_format(str(xml_file)) is True
        other = tmp_path / "o.xml"
        other.write_text("<root><a/></root>")
        assert adapter.detect_format(str(other)) is False


class TestSDMXJSONParsing:
    def test_series_layout_with_attributes(self):
        rows = list(SDMXAdapter.parse_sdmx_json(SERIES_JSON))
        assert len(rows) == 2
        first = rows[0]
        assert first["FREQ"] == "M" and first["FREQ_name"] == "Monthly"
        assert first["REF_AREA"] == "U2"
        assert first["TIME_PERIOD"] == "2024-01"
        assert first["Value"] == 1.09
        assert first["UNIT_MEASURE"] == "USD"
        assert first["OBS_STATUS"] == "A"
        assert rows[1]["TIME_PERIOD"] == "2024-02"
        assert "OBS_STATUS" not in rows[1]

    def test_flat_layout_v2_wrapper(self):
        rows = list(SDMXAdapter.parse_sdmx_json(FLAT_JSON_V2))
        assert len(rows) == 3
        assert [r.get("GEO") for r in rows] == ["DE", "FR", None]
        assert all(r["TIME_PERIOD"] == "2022" for r in rows)
        assert rows[0]["Value"] == 4000.5
        assert rows[1]["Value"] is None
        # index 2 has no matching GEO value: dimension left out, value kept
        assert "GEO" not in rows[2]
        assert rows[2]["Value"] == 1.0

    def test_parse_text_dispatches(self):
        adapter = SDMXAdapter(agency="ECB", flow="EXR")
        assert len(list(adapter.parse_text(json.dumps(SERIES_JSON)))) == 2
        assert len(list(adapter.parse_text(GENERIC_XML))) == 2
        with pytest.raises(ValidationError):
            list(adapter.parse_text("not json, not xml"))
        with pytest.raises(ValidationError):
            list(adapter.parse_text("<unclosed"))


class TestSDMXMLParsing:
    def test_generic(self):
        rows = list(SDMXAdapter.parse_sdmx_ml(GENERIC_XML))
        assert len(rows) == 2
        assert rows[0] == {
            "FREQ": "A", "REF_AREA": "US", "UNIT_MEASURE": "PC",
            "TIME_PERIOD": "2021", "Value": 5.5, "OBS_STATUS": "A",
        }
        assert rows[1]["TIME_PERIOD"] == "2022"
        assert rows[1]["Value"] != rows[1]["Value"]  # NaN parses to float nan

    def test_structure_specific_series_and_flat(self):
        rows = list(SDMXAdapter.parse_sdmx_ml(STRUCTURE_SPECIFIC_XML))
        assert len(rows) == 3
        assert rows[0] == {"FREQ": "Q", "REF_AREA": "JP", "UNIT_MEASURE": "JPY", "TIME_PERIOD": "2023-Q1", "Value": 100.25}
        assert rows[1]["Value"] == 101.0
        assert rows[2] == {"FREQ": "A", "REF_AREA": "CA", "TIME_PERIOD": "2023", "Value": 7.0}


class TestExtraction:
    @patch("data.importers.sdmx_adapter.requests.get")
    def test_extract_nodes_maps_to_indicator(self, mock_get):
        mock_get.return_value = Mock(text=json.dumps(SERIES_JSON), raise_for_status=Mock())
        adapter = SDMXAdapter(agency="ECB", flow="EXR", key="M.USD.EUR.SP00.A",
                              params={"startPeriod": "2024-01"})

        nodes = list(adapter.extract_nodes("sdmx:ECB:EXR:M.USD.EUR.SP00.A"))

        assert len(nodes) == 2
        node = nodes[0]
        assert node["_node_type"] == "SocialFabricIndicator"
        assert node["label"] == "EXR"
        assert node["current_value"] == 1.09
        assert node["meta"] == {
            "country": "U2", "period": "2024-01", "year": 2024, "frequency": "M",
            "unit": "USD", "agency": "ECB", "data_source": "SDMX:ECB",
        }
        kwargs = mock_get.call_args.kwargs
        assert kwargs["params"] == {"startPeriod": "2024-01"}
        assert "sdmx.data+json" in kwargs["headers"]["Accept"]

    @patch("data.importers.sdmx_adapter.requests.get")
    def test_observations_without_value_are_skipped(self, mock_get):
        mock_get.return_value = Mock(text=json.dumps(FLAT_JSON_V2), raise_for_status=Mock())
        adapter = SDMXAdapter(agency="EUROSTAT", flow="nama_10_gdp")
        nodes = list(adapter.extract_nodes("sdmx:EUROSTAT:nama_10_gdp"))
        assert [n["current_value"] for n in nodes] == [4000.5, 1.0]
        assert nodes[0]["meta"]["country"] == "DE"
        assert nodes[0]["meta"]["year"] == 2022

    def test_extract_from_local_xml_file(self, tmp_path):
        path = tmp_path / "gdp.xml"
        path.write_text(STRUCTURE_SPECIFIC_XML)
        adapter = SDMXAdapter(agency="IMF", flow="IFS")
        nodes = list(adapter.extract_nodes(str(path)))
        assert len(nodes) == 3
        assert nodes[0]["meta"]["country"] == "JP"
        assert nodes[0]["meta"]["period"] == "2023-Q1"
        assert nodes[0]["meta"]["year"] == 2023
        assert nodes[0]["meta"]["data_source"] == "SDMX:IMF"

    def test_extract_from_payload_dict(self):
        adapter = SDMXAdapter(agency="BIS", flow="WS_XRU")
        nodes = list(adapter.extract_nodes(SERIES_JSON))
        assert len(nodes) == 2 and nodes[0]["label"] == "WS_XRU"

    @patch("data.importers.sdmx_adapter.requests.get")
    def test_caching_and_rate_limit(self, mock_get):
        mock_get.return_value = Mock(text=json.dumps(FLAT_JSON_V2), raise_for_status=Mock())
        adapter = SDMXAdapter(agency="ECB", flow="EXR", rate_limit_delay=0)
        list(adapter.extract_nodes("sdmx:ECB:EXR"))
        list(adapter.extract_nodes("sdmx:ECB:EXR"))
        assert mock_get.call_count == 1

    @patch("data.importers.sdmx_adapter.time.sleep")
    @patch("data.importers.sdmx_adapter.requests.get")
    def test_request_failure_raises_validation_error(self, mock_get, _sleep):
        import requests as _requests
        mock_get.side_effect = _requests.ConnectionError("down")
        adapter = SDMXAdapter(agency="ECB", flow="EXR")
        with pytest.raises(ValidationError) as excinfo:
            list(adapter.extract_nodes("sdmx:ECB:EXR"))
        assert "SDMX request failed" in str(excinfo.value)
        assert mock_get.call_count == 3

    def test_relationships_unsupported_and_validate(self):
        adapter = SDMXAdapter(agency="ECB", flow="EXR")
        assert list(adapter.extract_relationships("sdmx:ECB:EXR")) == []
        assert adapter.validate_format("sdmx:ECB:EXR") == []
        adapter.flow = ""
        assert adapter.validate_format("sdmx:ECB:") == ["flow (dataflow id) is required for SDMX adapter"]


DATAFLOWS_XML = """<?xml version="1.0"?>
<message:Structure xmlns:message="http://www.sdmx.org/resources/sdmxml/schemas/v2_1/message"
                   xmlns:str="http://www.sdmx.org/resources/sdmxml/schemas/v2_1/structure"
                   xmlns:com="http://www.sdmx.org/resources/sdmxml/schemas/v2_1/common">
  <message:Structures><str:Dataflows>
    <str:Dataflow id="DSD_NAMAIN1@DF_QNA" agencyID="OECD.SDD.NAD" version="1.0">
      <com:Name xml:lang="fr">Comptes nationaux trimestriels</com:Name>
      <com:Name xml:lang="en">Quarterly national accounts</com:Name>
    </str:Dataflow>
    <str:Dataflow id="EXR" agencyID="ECB" version="1.0"><com:Name xml:lang="en">Exchange Rates</com:Name></str:Dataflow>
  </str:Dataflows></message:Structures>
</message:Structure>"""


class TestDataflowDiscovery:
    @patch("data.importers.sdmx_adapter.requests.get")
    def test_list_dataflows(self, mock_get):
        mock_get.return_value = Mock(text=DATAFLOWS_XML, raise_for_status=Mock())
        adapter = SDMXAdapter(agency="OECD", flow="", params={"startPeriod": "2020"})
        flows = adapter.list_dataflows()
        assert mock_get.call_args[0][0] == SDMX_AGENCIES["OECD"] + "/dataflow/all"
        assert mock_get.call_args.kwargs["params"] == {}       # data params not sent to /dataflow
        assert adapter.params == {"startPeriod": "2020"}         # and restored afterwards
        assert flows == [
            {"id": "DSD_NAMAIN1@DF_QNA", "agency": "OECD.SDD.NAD", "version": "1.0",
             "name": "Quarterly national accounts", "flow_ref": "OECD.SDD.NAD,DSD_NAMAIN1@DF_QNA,1.0"},
            {"id": "EXR", "agency": "ECB", "version": "1.0", "name": "Exchange Rates", "flow_ref": "ECB,EXR,1.0"},
        ]
        assert [f["id"] for f in adapter.list_dataflows(query="national")] == ["DSD_NAMAIN1@DF_QNA"]
        assert adapter.list_dataflows(query="nothing") == []

    @patch("data.importers.sdmx_adapter.requests.get")
    def test_list_dataflows_rejects_non_xml(self, mock_get):
        mock_get.return_value = Mock(text="{}", raise_for_status=Mock())
        with pytest.raises(ValidationError):
            SDMXAdapter(agency="ECB", flow="").list_dataflows()


class TestMappingTemplate:
    def test_sdmx_indicator_template_year_and_period(self):
        mapping = MappingTemplates.sdmx_indicator()
        row = mapping.transform_row({"dataflow": "F", "Value": "3", "TIME_PERIOD": "1999-Q4", "country": "de"})
        assert row["current_value"] == 3.0
        assert row["meta"]["period"] == "1999-Q4"
        assert row["meta"]["year"] == 1999
        assert row["meta"]["country"] == "DE"
        assert row["meta"]["data_source"] == "SDMX"
        with pytest.raises(KeyError):
            mapping.transform_row({"Value": 1})
