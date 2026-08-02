Feature: Production Hardening
  Como Luis Daniel
  Quiero que el sistema opere sin mi intervención
  Para que Abraham reciba datos frescos sin que yo tenga que acordarme

  Scenario: Sync corre cada 6h
    Given el cron esta instalado
    When pasa el intervalo de 6h
    Then data/abe-music.json tiene last_sync actualizado

  Scenario: Lead bridge funcional
    Given Neo4j esta online
    When sync detecta un artista con streams >= 1M
    Then el lead se crea en Neo4j sin error de import

  Scenario: Commit sin spec activa
    Given no hay spec en process/active/
    When ejecuto git commit
    Then el commit pasa sin --no-verify

  Scenario: Qdrant responde queries
    Given Qdrant esta online
    When busco "Hector Rubio" en coleccion abe-artists
    Then recibo datos del artista

  Scenario: Dashboard salud muestra providers
    Given el ABE Service esta corriendo
    When consulto /health/providers
    Then recibo estado de cada provider (ok/warn/fail)

  Scenario: Wikipedia 403 no bloquea el sync
    Given Wikipedia responde 403
    When sync corre
    Then el resto de los collectors ejecutan normalmente
    And wikipedia_api aparece como degraded en dashboard
