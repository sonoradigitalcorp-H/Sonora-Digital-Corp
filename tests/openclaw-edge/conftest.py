"""
Fixtures compartidos para tests de OpenClaw Edge
"""

import pytest

SAMPLE_CFDI_VALID = """<?xml version="1.0" encoding="UTF-8"?>
<cfdi:Comprobante
  xmlns:cfdi="http://www.sat.gob.mx/cfd/4"
  xmlns:tfd="http://www.sat.gob.mx/TimbreFiscalDigital"
  Version="4.0"
  TipoDeComprobante="I"
  Fecha="2026-07-15T10:30:00"
  RfcEmisor="FGA970101AAA"
  NombreEmisor="Fourgea Mexico SA de CV"
  RfcReceptor="XIA190128TA7"
  NombreReceptor="Cliente Ejemplo SA"
  SubTotal="1000.00"
  Total="1160.00"
  Moneda="MXN">
  <cfdi:Emisor Rfc="FGA970101AAA" Nombre="Fourgea Mexico SA de CV" RegimenFiscal="601"/>
  <cfdi:Receptor Rfc="XIA190128TA7" Nombre="Cliente Ejemplo SA" DomicilioFiscalReceptor="12345" RegimenFiscalReceptor="601" UsoCFDI="G03"/>
  <cfdi:Conceptos>
    <cfdi:Concepto ClaveProdServ="84111506" Cantidad="1" ClaveUnidad="E48" Descripcion="Servicios contables" ValorUnitario="1000.00" Importe="1000.00">
      <cfdi:Impuestos>
        <cfdi:Traslados>
          <cfdi:Traslado Base="1000.00" Impuesto="002" TipoFactor="Tasa" TasaOCuota="0.160000" Importe="160.00"/>
        </cfdi:Traslados>
      </cfdi:Impuestos>
    </cfdi:Concepto>
  </cfdi:Conceptos>
  <cfdi:Impuestos TotalImpuestosTrasladados="160.00">
    <cfdi:Traslados>
      <cfdi:Traslado Base="1000.00" Impuesto="002" TipoFactor="Tasa" TasaOCuota="0.160000" Importe="160.00"/>
    </cfdi:Traslados>
  </cfdi:Impuestos>
  <cfdi:Complemento>
    <tfd:TimbreFiscalDigital UUID="12345678-1234-1234-1234-123456789abc" FechaTimbrado="2026-07-15T10:30:01" RfcProvCertif="SAT970701NN3"/>
  </cfdi:Complemento>
</cfdi:Comprobante>"""

SAMPLE_CFDI_RFC_INVALID = """<?xml version="1.0" encoding="UTF-8"?>
<cfdi:Comprobante
  xmlns:cfdi="http://www.sat.gob.mx/cfd/4"
  Version="4.0"
  TipoDeComprobante="I"
  Fecha="2026-07-15T10:30:00"
  RfcEmisor="RFCINVALIDO"
  RfcReceptor="XIA190128TA7"
  SubTotal="1000.00"
  Total="1160.00"
  Moneda="MXN">
  <cfdi:Conceptos>
    <cfdi:Concepto ClaveProdServ="84111506" Cantidad="1" ClaveUnidad="E48" Descripcion="Servicio" ValorUnitario="1000.00" Importe="1000.00"/>
  </cfdi:Conceptos>
</cfdi:Comprobante>"""

SAMPLE_CFDI_NEGATIVE_TOTAL = """<?xml version="1.0" encoding="UTF-8"?>
<cfdi:Comprobante
  xmlns:cfdi="http://www.sat.gob.mx/cfd/4"
  Version="4.0"
  TipoDeComprobante="E"
  Fecha="2026-07-15T10:30:00"
  RfcEmisor="FGA970101AAA"
  RfcReceptor="XIA190128TA7"
  SubTotal="1000.00"
  Total="-500.00"
  Moneda="MXN">
  <cfdi:Conceptos>
    <cfdi:Concepto ClaveProdServ="84111506" Cantidad="1" ClaveUnidad="E48" Descripcion="Nota de credito" ValorUnitario="1000.00" Importe="1000.00"/>
  </cfdi:Conceptos>
</cfdi:Comprobante>"""

SAMPLE_XML_BROKEN = b"<xml>this is broken>"


@pytest.fixture
def sample_cfdi_valid_xml():
    return SAMPLE_CFDI_VALID.encode("utf-8")


@pytest.fixture
def sample_cfdi_invalid_rfc_xml():
    return SAMPLE_CFDI_RFC_INVALID.encode("utf-8")


@pytest.fixture
def sample_cfdi_negative_xml():
    return SAMPLE_CFDI_NEGATIVE_TOTAL.encode("utf-8")


@pytest.fixture
def sample_xml_broken():
    return SAMPLE_XML_BROKEN
