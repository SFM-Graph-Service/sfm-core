"""
SDMX 2.1 import adapter.

Pulls statistical observations from any SDMX 2.1 REST endpoint (ECB, Eurostat,
BIS, IMF, ILO, OECD, UN, World Bank) or from a local SDMX file, and maps them to
SocialFabricIndicator nodes. Two wire formats are understood:

- SDMX-JSON (1.0 and 2.0), in both the series-keyed and flat-observation layouts
- SDMX-ML 2.1 data messages, both Generic and StructureSpecific

Source references take the form ``sdmx:AGENCY:FLOW[:KEY]`` where AGENCY is a
known agency code or a full base URL, FLOW is the dataflow id and KEY the
dot-separated dimension key (``all`` for everything).
"""

from __future__ import annotations

import json
import time
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Tuple, Union
from urllib.parse import urlparse

import requests

from .base_adapter import BaseImportAdapter, ImportConfig
from .mapping_config import MappingConfig
from .validators import ValidationError


KNOWN_AGENCIES: Dict[str, str] = {
    "ECB": "https://data-api.ecb.europa.eu/service",
    "EUROSTAT": "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1",
    "BIS": "https://stats.bis.org/api/v1",
    "IMF": "https://sdmxcentral.imf.org/ws/public/sdmxapi/rest",
    "ILO": "https://sdmx.ilo.org/rest",
    "OECD": "https://sdmx.oecd.org/public/rest",
    "UNSD": "https://data.un.org/ws/rest",
    "WB": "https://api.worldbank.org/v2/sdmx/rest",
}

SDMX_JSON_ACCEPT = "application/vnd.sdmx.data+json;version=1.0.0, application/json;q=0.9, application/xml;q=0.8"

# Dimension ids that, when present, identify the reporting country / area
_COUNTRY_DIMENSIONS = ("REF_AREA", "LOCATION", "GEO", "geo", "COUNTRY", "REPORTING_AREA", "AREA")


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _to_number(value: Any) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(str(value).strip())
    except ValueError:
        return None


class SDMXAdapter(BaseImportAdapter):
    """Import adapter for SDMX 2.1 REST services and SDMX files."""

    def __init__(
        self,
        agency: str,
        flow: str,
        key: str = "all",
        params: Optional[Dict[str, str]] = None,
        mapping: Optional[MappingConfig] = None,
        config: Optional[ImportConfig] = None,
        rate_limit_delay: float = 0.5,
    ):
        """
        Args:
            agency: Known agency code (see KNOWN_AGENCIES) or a full SDMX REST base URL
            flow: Dataflow id, e.g. "EXR" (ECB), "nama_10_gdp" (Eurostat)
            key: Dot-separated dimension key, e.g. "M.USD.EUR.SP00.A"; "all" for no filter
            params: Extra query parameters, e.g. {"startPeriod": "2020", "endPeriod": "2024"}
            mapping: Field mapping (defaults to MappingTemplates.sdmx_indicator())
            config: Import configuration
            rate_limit_delay: Minimum seconds between requests
        """
        super().__init__(config)
        self.agency, self.base_url = self._resolve_agency(agency)
        self.flow = flow
        self.key = key or "all"
        self.params = dict(params or {})
        self.mapping = mapping or self._default_mapping()
        self.rate_limit_delay = rate_limit_delay
        self._last_request_time = 0.0
        self._cache: Dict[str, str] = {}

    @staticmethod
    def _resolve_agency(agency: str) -> Tuple[str, str]:
        if not agency:
            raise ValueError("agency is required (a known code or an SDMX REST base URL)")
        if agency.lower().startswith(("http://", "https://")):
            host = urlparse(agency).hostname or agency
            return host, agency.rstrip("/")
        code = agency.upper()
        if code not in KNOWN_AGENCIES:
            raise ValueError(
                f"Unknown SDMX agency '{agency}'. Known: {', '.join(sorted(KNOWN_AGENCIES))}, "
                "or pass a full base URL"
            )
        return code, KNOWN_AGENCIES[code]

    def _default_mapping(self) -> MappingConfig:
        from .mapping_config import MappingTemplates
        return MappingTemplates.sdmx_indicator()

    # ------------------------------------------------------------------ format

    def detect_format(self, source: Union[str, Path, Dict[str, Any]]) -> bool:
        if isinstance(source, dict):
            return "dataSets" in source or "dataSets" in source.get("data", {}) or "flow" in source
        if isinstance(source, Path) or (isinstance(source, str) and not source.startswith("sdmx:")):
            path = Path(source)
            if path.suffix.lower() in (".xml", ".json") and path.is_file():
                head = path.read_text(encoding="utf-8", errors="ignore")[:4096]
                return "sdmx" in head.lower() or '"dataSets"' in head
            return False
        return isinstance(source, str) and source.startswith("sdmx:")

    def validate_format(self, source: Union[str, Path, Dict[str, Any]]) -> List[str]:
        errors = []
        if not self.flow:
            errors.append("flow (dataflow id) is required for SDMX adapter")
        return errors

    # ------------------------------------------------------------- extraction

    def extract_nodes(self, source: Union[str, Path, Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
        try:
            for obs in self._observations(source):
                if obs.get("Value") is None:
                    continue
                try:
                    yield self.mapping.transform_row(obs)
                except (KeyError, ValueError) as e:
                    if not self.config.continue_on_error:
                        raise ValueError(f"Failed to map observation: {e}") from e
        except requests.RequestException as e:
            raise ValidationError(f"SDMX request failed: {e}") from e

    def extract_relationships(self, source: Union[str, Path, Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
        return iter([])

    def _observations(self, source: Union[str, Path, Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
        if isinstance(source, dict):
            yield from self._annotate(self.parse_sdmx_json(source))
            return

        if isinstance(source, str) and source.startswith("sdmx:"):
            parts = source.split(":", 3)
            if len(parts) >= 3 and parts[1]:
                self.agency, self.base_url = self._resolve_agency(parts[1])
            if len(parts) >= 3 and parts[2]:
                self.flow = parts[2]
            if len(parts) == 4 and parts[3]:
                self.key = parts[3]
            text = self._fetch(self.build_url())
            yield from self._annotate(self.parse_text(text))
            return

        path = Path(source)
        if path.is_file():
            yield from self._annotate(self.parse_text(path.read_text(encoding="utf-8")))
            return

        text = self._fetch(self.build_url())
        yield from self._annotate(self.parse_text(text))

    def build_url(self) -> str:
        return f"{self.base_url}/data/{self.flow}/{self.key}"

    def _fetch(self, url: str, max_retries: int = 3) -> str:
        cache_key = f"{url}?{sorted(self.params.items())}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        elapsed = time.time() - self._last_request_time
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)

        for attempt in range(max_retries):
            try:
                response = requests.get(
                    url,
                    params=self.params,
                    headers={"Accept": SDMX_JSON_ACCEPT},
                    timeout=60,
                )
                response.raise_for_status()
                self._last_request_time = time.time()
                text: str = response.text
                self._cache[cache_key] = text
                return text
            except requests.RequestException:
                if attempt == max_retries - 1:
                    raise
                time.sleep(2 ** attempt)

        raise ValidationError(f"Failed to fetch SDMX data after {max_retries} retries")

    def _annotate(self, observations: Iterator[Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
        fetched_at = datetime.now().isoformat()
        for obs in observations:
            obs.setdefault("dataflow", self.flow)
            obs["agency"] = self.agency
            obs["data_source"] = f"SDMX:{self.agency}"
            obs["fetched_at"] = fetched_at
            for dim in _COUNTRY_DIMENSIONS:
                if obs.get(dim):
                    obs["country"] = obs[dim]
                    break
            yield obs

    # ---------------------------------------------------------------- parsing

    def parse_text(self, text: str) -> Iterator[Dict[str, Any]]:
        stripped = text.lstrip()
        if stripped.startswith("<"):
            return self.parse_sdmx_ml(stripped)
        try:
            payload = json.loads(stripped)
        except json.JSONDecodeError as e:
            raise ValidationError(f"SDMX response is neither JSON nor XML: {e}") from e
        return self.parse_sdmx_json(payload)

    @staticmethod
    def parse_sdmx_json(payload: Dict[str, Any]) -> Iterator[Dict[str, Any]]:
        """Flatten an SDMX-JSON message (1.0 or 2.0; series-keyed or flat) into observation dicts."""
        data = payload.get("data", payload)
        structure = data.get("structure")
        if structure is None:
            structures = data.get("structures") or []
            structure = structures[0] if structures else {}

        dims = structure.get("dimensions", {})
        dataset_dims = dims.get("dataSet", [])
        series_dims = dims.get("series", [])
        obs_dims = dims.get("observation", [])
        attrs = structure.get("attributes", {})
        series_attrs = attrs.get("series", [])
        obs_attrs = attrs.get("observation", [])

        def decode(dim_list: List[Dict[str, Any]], key: str) -> Dict[str, Any]:
            out: Dict[str, Any] = {}
            indices = key.split(":")
            for i, dim in enumerate(dim_list):
                if i >= len(indices):
                    break
                try:
                    idx = int(indices[i])
                except ValueError:
                    continue
                values = dim.get("values", [])
                if idx < len(values):
                    value = values[idx]
                    dim_id = dim.get("id", f"DIM_{i}")
                    out[dim_id] = value.get("id")
                    if value.get("name"):
                        out[f"{dim_id}_name"] = value["name"]
            return out

        def decode_attrs(attr_list: List[Dict[str, Any]], attr_values: List[Any]) -> Dict[str, Any]:
            out: Dict[str, Any] = {}
            for i, attr in enumerate(attr_list):
                if i >= len(attr_values) or attr_values[i] is None:
                    continue
                values = attr.get("values", [])
                idx = attr_values[i]
                if isinstance(idx, int) and idx < len(values):
                    value = values[idx]
                    out[attr.get("id", f"ATTR_{i}")] = value.get("id", value.get("name"))
                elif not isinstance(idx, int):
                    out[attr.get("id", f"ATTR_{i}")] = idx
            return out

        fixed: Dict[str, Any] = {}
        for dim in dataset_dims:
            values = dim.get("values", [])
            if values:
                fixed[dim.get("id", "")] = values[0].get("id")

        for dataset in data.get("dataSets", []):
            for series_key, series in (dataset.get("series") or {}).items():
                base = dict(fixed)
                base.update(decode(series_dims, series_key))
                base.update(decode_attrs(series_attrs, series.get("attributes") or []))
                for obs_key, obs_values in (series.get("observations") or {}).items():
                    obs = dict(base)
                    obs.update(decode(obs_dims, obs_key))
                    obs["Value"] = _to_number(obs_values[0]) if obs_values else None
                    obs.update(decode_attrs(obs_attrs, list(obs_values[1:]) if obs_values else []))
                    yield obs

            for obs_key, obs_values in (dataset.get("observations") or {}).items():
                obs = dict(fixed)
                obs.update(decode(obs_dims, obs_key))
                obs["Value"] = _to_number(obs_values[0]) if obs_values else None
                obs.update(decode_attrs(obs_attrs, list(obs_values[1:]) if obs_values else []))
                yield obs

    @staticmethod
    def parse_sdmx_ml(text: str) -> Iterator[Dict[str, Any]]:
        """Flatten an SDMX-ML 2.1 data message (Generic or StructureSpecific) into observation dicts."""
        try:
            root = ET.fromstring(text)
        except ET.ParseError as e:
            raise ValidationError(f"Invalid SDMX-ML: {e}") from e

        datasets = [el for el in root.iter() if _local(el.tag) == "DataSet"] or [root]

        def key_values(container: ET.Element) -> Dict[str, Any]:
            return {
                v.get("id", ""): v.get("value")
                for v in container
                if _local(v.tag) == "Value" and v.get("id")
            }

        def parse_obs(obs: ET.Element, base: Dict[str, Any]) -> Dict[str, Any]:
            out = dict(base)
            children = list(obs)
            if any(_local(c.tag) == "ObsValue" for c in children):
                for child in children:
                    name = _local(child.tag)
                    if name == "ObsDimension":
                        out[child.get("id", "TIME_PERIOD")] = child.get("value")
                    elif name == "ObsValue":
                        out["Value"] = _to_number(child.get("value"))
                    elif name == "Attributes":
                        out.update(key_values(child))
            else:
                out.update(obs.attrib)
                out["Value"] = _to_number(out.pop("OBS_VALUE", None))
            return out

        for dataset in datasets:
            for element in dataset:
                name = _local(element.tag)
                if name == "Series":
                    base: Dict[str, Any] = {}
                    if any(_local(c.tag) == "SeriesKey" for c in element):
                        for child in element:
                            if _local(child.tag) in ("SeriesKey", "Attributes"):
                                base.update(key_values(child))
                    else:
                        base.update(element.attrib)
                    for obs in element:
                        if _local(obs.tag) == "Obs":
                            yield parse_obs(obs, base)
                elif name == "Obs":
                    yield parse_obs(element, {})
