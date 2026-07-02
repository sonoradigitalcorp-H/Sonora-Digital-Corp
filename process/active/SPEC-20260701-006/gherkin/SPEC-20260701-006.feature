Feature: CI Completo — Mock Tests para Collectors
  Como Luis Daniel
  Quiero que cada collector tenga tests automatizados en CI
  Para que no haya regression silenciosa cuando cambie algo

  Scenario: Deezer collector con mock HTTP
    Given el collector deezer.py tiene mock de httpx
    When llamo fetch_artist("Hector Rubio")
    Then retorna dict con followers, nb_album, top_tracks

  Scenario: Apple Music collector con mock HTTP
    Given el collector apple_music.py tiene mock de httpx
    When llamo search_artist("Hector Rubio")
    Then retorna dict con apple_music_id y apple_music_url

  Scenario: YouTube collector con mock CLI
    Given el collector youtube.py tiene mock de subprocess
    When llamo search_artist("Hector Rubio")
    Then retorna dict con youtube_total_views_search

  Scenario: TikTok collector con mock Playwright
    Given el collector tiktok.py tiene mock de playwright
    When llamo fetch_profile("jesusurquijo")
    Then retorna dict con tiktok_followers

  Scenario: Spotify collector con mock Playwright
    Given el collector spotify.py tiene mock de playwright
    When llamo fetch_artist_metrics("spotify_url")
    Then retorna dict con spotify_monthly_listeners

  Scenario: Wikipedia collector con mock HTTP
    Given el collector wikipedia.py tiene mock de httpx
    When llamo fetch_bio("Hector Rubio")
    Then retorna dict con bio y wikipedia_url

  Scenario: sync.py fallback chain
    Given execute_capability devuelve error para Deezer
    When sync corre con fallback=True
    Then Apple Music es ejecutado como fallback

  Scenario: Health cache persiste
    Given check_provider_health es llamado
    When get_provider_health es llamado con mismo ID
    Then retorna el mismo objeto ProviderHealth
