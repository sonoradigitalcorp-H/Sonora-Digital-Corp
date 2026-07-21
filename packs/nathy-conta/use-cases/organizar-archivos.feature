Feature: Organizar archivos
  La contadora puede ordenar los XMLs y PDFs desordenados en su laptop

  Scenario: Organizar carpeta con 50 archivos mezclados
    Given la carpeta "C:\Users\Nathy\Downloads" tiene 50 archivos
    And están mezclados XMLs de 3 clientes diferentes
    When se ejecuta organizador
    Then se crean 3 carpetas de cliente
    And cada XML se renombra: {RFC}_{FECHA}_{TIPO}_{UUID}.xml
    And los PDFs se agrupan con sus XMLs correspondientes
    And la carpeta origen queda vacía

  Scenario: Detectar duplicados
    Given hay 2 archivos XML con el mismo UUID
    When se organiza
    Then se mueve 1 a la carpeta del cliente
    And el duplicado se mueve a "Duplicados/"

  Scenario: XML sin PDF relacionado
    Given hay un XML sin PDF de la misma factura
    When se organiza
    Then el XML se mueve a carpeta del cliente
    And se marca como "sin PDF asociado"
