# language: es
Caracteristica: Aislamiento Multi-Tenant (El Sigilo del Tenant)
  Como cliente de Sonora Digital Corp
  Quiero que mis datos esten completamente aislados de otros clientes
  Para que ningun competidor o tercero pueda acceder a mi informacion

  Antecedentes:
    Dado que existen 3 tenants activos: "clinica-smile", "restaurante-luna", "barberia-norte"
    Y cada tenant tiene su UUID unico en PostgreSQL
    Y Row Level Security esta configurado en todas las tablas
    Y los caches en Redis estan prefijados por tenant_id
    Y los indices en Qdrant estan separados por tenant

  Escenario: Datos de llamadas aislados entre tenants
    Dado que el tenant "clinica-smile" recibe una llamada de Maria
    Y el tenant "restaurante-luna" recibe una llamada de Pedro
    Cuando el cliente de "clinica-smile" consulta sus llamadas
    Entonces solo ve la llamada de Maria
    Y NO ve la llamada de Pedro
    Y el query SQL incluye automaticamente el filtro tenant_id
    Y el tiempo de query no aumenta por el filtro RLS (< 5ms overhead)

  Escenario: Knowledge bases aisladas
    Dado que "clinica-smile" tiene KB de odontologia
    Y "restaurante-luna" tiene KB de gastronomia
    Cuando el agente de "clinica-smile" busca informacion sobre "menu"
    Entones encuentra resultados sobre "menu de procedimientos dentales" (su KB)
    Y NO encuentra resultados sobre "menu de restaurante" (KB del otro tenant)
    Y la busqueda semantica en Qdrant solo consulta la coleccion del tenant

  Escenario: Configuracion de voz aislada
    Dado que "clinica-smile" tiene voz clonada del Dr. Martinez
    Y "barberia-norte" tiene voz clonada de Don Felipe
    Cuando el agente de "clinica-smile" genera una respuesta de voz
    Entonces usa la voz del Dr. Martinez
    Y NO puede acceder al archivo de voz de Don Felipe
    Y los archivos de voz estan en directorios separados por tenant

  Escenario: Cache Redis aislado
    Dado que el tenant "clinica-smile" almacena sesion de Maria en Redis
    Cuando el tenant "restaurante-luna" consulta sesiones activas
    Entonces NO ve la sesion de Maria
    Y la clave en Redis es "tenant:{uuid}:session:{session_id}"
    Y un scan de keys con "tenant:{other_uuid}:*" retorna 0 resultados

  Escenario: Metricas y dashboards aislados
    Dado que "clinica-smile" tiene 50 llamadas hoy
    Y "restaurante-luna" tiene 30 llamadas hoy
    Cuando el owner de "clinica-smile" abre su dashboard
    Entonces ve 50 llamadas
    Y NO puede ver las 30 llamadas del restaurante
    Y Mystic (admin) ve los 80 llamadas totales

  Escenario: Intento de acceso cruzado (ataque)
    Dado que un usuario malicioso del tenant "clinica-smile"
    Y envia un API request con tenant_id de "restaurante-luna"
    Cuando el API Gateway procesa la request
    Entonces compara el tenant_id del JWT con el tenant_id del request
    Y detecta mismatch
    Y retorna HTTP 403 Forbidden
    Y registra el intento en el log de seguridad
    Y envia alerta WARNING por Telegram a Mystic