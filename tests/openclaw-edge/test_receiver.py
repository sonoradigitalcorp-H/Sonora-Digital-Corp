"""
Tests para Edge Receiver — procesamiento de XML CFDI
"""

from apps.openclaw_edge.receiver import (
    _classify_cfdi,
    _generate_filename,
    _parse_cfdi_xml,
    _to_float,
)


class TestParseCFDI:
    def test_valid_cfdi(self, sample_cfdi_valid_xml):
        result = _parse_cfdi_xml(sample_cfdi_valid_xml, "factura.xml")
        assert result["valid"] is True
        assert result["rfc_emisor"] == "FGA970101AAA"
        assert result["rfc_receptor"] == "XIA190128TA7"
        assert result["total"] == 1160.00
        assert result["subtotal"] == 1000.00
        assert result["iva"] == 160.00
        assert result["uuid"] == "12345678-1234-1234-1234-123456789abc"
        assert result["tipo"] == "I"
        assert result["version"] == "4.0"
        assert len(result["conceptos"]) == 1
        assert result["errors"] == []

    def test_invalid_rfc_rejected(self, sample_cfdi_invalid_rfc_xml):
        result = _parse_cfdi_xml(sample_cfdi_invalid_rfc_xml, "mala.xml")
        assert result["valid"] is False
        assert "RFC emisor" in str(result["errors"])

    def test_negative_total_rejected(self, sample_cfdi_negative_xml):
        result = _parse_cfdi_xml(sample_cfdi_negative_xml, "negativa.xml")
        assert result["valid"] is False
        assert any("negativo" in e.lower() for e in result["errors"])

    def test_broken_xml_returns_error(self, sample_xml_broken):
        result = _parse_cfdi_xml(sample_xml_broken, "roto.xml")
        assert result["valid"] is False
        assert len(result["errors"]) >= 1

    def test_conceptos_parsed(self, sample_cfdi_valid_xml):
        result = _parse_cfdi_xml(sample_cfdi_valid_xml, "factura.xml")
        concepto = result["conceptos"][0]
        assert concepto["descripcion"] == "Servicios contables"
        assert concepto["importe"] == 1000.00
        assert "0.160000" in concepto.get("tasas_iva", [])

    def test_impuestos_totales(self, sample_cfdi_valid_xml):
        result = _parse_cfdi_xml(sample_cfdi_valid_xml, "factura.xml")
        assert result["impuestos"]["total_traslados"] == 160.00


class TestToFloat:
    def test_valid_number(self):
        assert _to_float("1000.50") == 1000.50

    def test_invalid_number_returns_zero(self):
        assert _to_float("abc") == 0.0

    def test_none_returns_zero(self):
        assert _to_float(None) == 0.0

    def test_empty_string_returns_zero(self):
        assert _to_float("") == 0.0


class TestClassification:
    def test_ingreso(self):
        assert _classify_cfdi({"tipo": "I"}) == "ingreso"

    def test_egreso(self):
        assert _classify_cfdi({"tipo": "E"}) == "egreso"

    def test_nomina(self):
        assert _classify_cfdi({"tipo": "P"}) == "nomina"
        assert _classify_cfdi({"tipo": "N"}) == "nomina"

    def test_traslado(self):
        assert _classify_cfdi({"tipo": "T"}) == "traslado"

    def test_default(self):
        assert _classify_cfdi({"tipo": "X"}) == "otro"


class TestFilenameGeneration:
    def test_standard_filename(self):
        data = {
            "rfc_emisor": "FOURGEAMEXICO",
            "fecha": "2026-07-15T10:30:00",
            "uuid": "12345678-1234-1234-1234-123456789abc",
            "tipo": "I",
        }
        name = _generate_filename(data)
        assert name.startswith("FOURGEAMEXICO_20260715")
        assert "INGRESO" in name
        assert "12345678" in name
        assert name.endswith(".xml")

    def test_missing_rfc(self):
        data = {"fecha": "2026-01-01", "uuid": "abc", "tipo": "E"}
        name = _generate_filename(data)
        assert name.startswith("SINRFC")

    def test_missing_uuid(self):
        data = {"rfc_emisor": "AAA010101AAA", "fecha": "2026-01-01", "tipo": "I"}
        name = _generate_filename(data)
        assert "SINUUID" in name
