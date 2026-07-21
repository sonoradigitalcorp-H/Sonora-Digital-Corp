# language: es
Funcionalidad: Auto-captura de comandos Bash en Engram
  Como desarrollador de Sonora Digital Corp
  Quiero que mis comandos relevantes se guarden automáticamente en Engram
  Para tener historial completo sin esfuerzo manual

  Escenario: Captura comando git commit
    Dado que estoy en el directorio del proyecto "sonora-digital-corp"
    Y tengo una sesión Engram activa
    Cuando ejecuto "git commit -m 'feat: add user auth'"
    Entonces se guarda una observación en Engram con:
      | campo          | valor                          |
      | title          | "cmd: git commit -m 'feat: add user auth'" |
      | type           | "command"                      |
      | topic_key      | "commands/20260718"            |
      | project        | "sonora-digital-corp"          |
      | content contiene | "git commit -m 'feat: add user auth'" |
      | content contiene | "exit_code: 0"                 |

  Escenario: No captura comando de solo lectura
    Dado que estoy en el directorio del proyecto
    Cuando ejecuto "ls -la"
    Entonces no se guarda ninguna observación en Engram

  Escenario: No captura cat, grep, pwd, cd
    Dado que estoy en el directorio del proyecto
    Cuando ejecuto "cat README.md"
    Entonces no se guarda observación
    Cuando ejecuto "grep 'TODO' *.py"
    Entonces no se guarda observación
    Cuando ejecuto "pwd"
    Entonces no se guarda observación
    Cuando ejecuto "cd /tmp"
    Entonces no se guarda observación

  Escenario: Captura comandos de build/deploy
    Dado que estoy en el directorio del proyecto
    Cuando ejecuto "npm run build"
    Entonces se guarda observación tipo "command"
    Cuando ejecuto "docker compose up -d"
    Entonces se guarda observación tipo "command"
    Cuando ejecuto "python3 scripts/deploy.py"
    Entonces se guarda observación tipo "command"

  Escenario: Rate limit 30 por minuto
    Dado que ejecuto 35 comandos relevantes en 60 segundos
    Cuando pasa el minuto
    Entonces solo se guardan las primeras 30 observaciones
    Y las 5 restantes se descartan silenciosamente

  Escenario: Filtra secrets del contenido
    Dado que ejecuto "export API_SECRET=sk-12345 && python3 script.py"
    Cuando se guarda la observación
    Entonces el contenido no contiene "sk-12345"
    Y el contenido contiene "[FILTERED]" en su lugar