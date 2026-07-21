# Manual de Usuario — ABE Music PWA

## ¿Qué es?
Aplicación Web Progresiva (PWA) para artistas de ABE Music. Dashboard de estado del sistema, revenue, contratos y más.

## Acceso
- **URL**: http://149.56.46.173:5180/pwa/
- **Instalar**: Abrir en Chrome → ⋮ → "Instalar ABE Music OS"
- **Funciona offline**: Sí (service worker cache)

## Funcionalidades
### Dashboard de Estado
Muestra salud de todos los servicios del ecosistema.
- Verde = operativo
- Rojo = caído
- Amarillo = degradado

### Revenue
Consulta streams y revenue por artista.
- Hector Rubio: ~$460K (115M streams)
- Jesus Urquijo: ~$18.5K (4.6M streams)
- Javier Arvayo: ~$200 (50K streams)

### Contratos
Visualiza contratos activos y su estado.

## Troubleshooting
- **No carga**: Verificar que ABE Service esté corriendo (`:5180`)
- **Datos desactualizados**: Esperar sync automático (cada 30 min)
- **Error de conexión**: Revisar internet o forwarding SSH
