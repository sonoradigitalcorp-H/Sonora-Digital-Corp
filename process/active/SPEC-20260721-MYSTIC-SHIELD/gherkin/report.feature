Feature: Reportes y reenvío de diagnósticos
  As a CEO
  I want poder consultar y reenviar diagnósticos anteriores
  So that pueda compartir la información con mi equipo

  Background:
    Given existe un diagnóstico previo con ID "abc12345"
    And el reporte está almacenado en state/reports/abc12345.json

  Scenario: Consultar reporte por ID via API
    When GET /api/report/abc12345
    Then response status es 200
    And el JSON contiene: diagnosis_id, company_name, scan, analysis, pdf_path, whatsapp, email

  Scenario: Reporte no encontrado
    When GET /api/report/id-inexistente
    Then response status es 404
    And el error indica "Report not found"

  Scenario: Listar reportes recientes
    When GET /api/reports?limit=5
    Then response contiene array reports con máximo 5 entries
    And cada entry tiene: id, company_name, timestamp, total_hosts, active_hosts

  Scenario: Reenviar reporte por WhatsApp
    Given el reporte "abc12345" existe
    And el CEO tiene WhatsApp "6622681111"
    When ejecuto shield_send_report("abc12345", ceo_phone="6622681111")
    Then se reenvía el PDF + audio + mensaje introductorio
    And se confirma "whatsapp_sent: true"

  Scenario: Reenviar reporte que no existe
    Given el ID "no-existe" no tiene reporte
    When ejecuto shield_send_report("no-existe")
    Then el resultado indica error "Report no-existe not found"
