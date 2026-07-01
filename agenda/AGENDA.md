# Agenda — Native Agent OS: ABE Music Productivización

**Inicio**: 2026-07-01
**Ritmo**: 5 días/semana, 4-6 horas diarias

---

## Filosofía

- Cada día tiene un tema, un entregable y una métrica
- Alternamos: un día construcción, un día negocio
- Los viernes son de integración y deploy
- Semanal: release a producción

---

## Semana 1: Fundación

### Lunes — Setup
| Quién | Actividad | Entregable |
|-------|-----------|------------|
| **Mystic** | Conectar fal.ai API, Seedance, sandbox CI | media.js + sandbox.js funcionando |
| **Abraham** | Crear cuenta Spotify Developer, obtener API keys | Client ID + Secret listos |
| **Juntos** | Subir 1 canción real a ABE Music | Release real en el sistema |

### Martes — Datos Reales
| Quién | Actividad | Entregable |
|-------|-----------|------------|
| **Mystic** | Conectar Spotify API de Abraham, pipeline de sync automático | artist_sync jalando datos reales |
| **Abraham** | Ingresar datos históricos de artistas vía intake | streams, revenue, releases históricos |
| **Juntos** | Verificar que los datos en dashboard coinciden con la realidad | Dashboard mostrando datos reales |

### Miércoles — Contenido
| Quién | Actividad | Entregable |
|-------|-----------|------------|
| **Mystic** | Pipeline de generación de contenido + portadas AI | media tools funcionando con fal.ai |
| **Abraham** | Crear briefs de contenido para redes sociales | 5 briefs listos |
| **Juntos** | Generar primera portada de álbum con AI | Portada lista para release |

### Jueves — Automatización
| Quién | Actividad | Entregable |
|-------|-----------|------------|
| **Mystic** | Workflows automáticos: reporte semanal, sync diario, alertas | 3 workflows automáticos corriendo |
| **Abraham** | Configurar notificaciones: qué quiere saber y cuándo | Preferencias de alertas |
| **Juntos** | Testear que las alertas llegan a Telegram | Alerta funcionando |

### Viernes — Release
| Quién | Actividad | Entregable |
|-------|-----------|------------|
| **Mystic** | Sandbox full, fixes, deploy a producción | Release v1.0 |
| **Abraham** | Aprobar release, invitar a 1 artista a usar el sistema | Primer artista usando ABE SaaS |
| **Juntos** | Review semanal, ajustar agenda para semana 2 | Semana 1 completada |

---

## Semana 2: Crecimiento

### Lunes — Artistas
| Quién | Actividad | Entregable |
|-------|-----------|------------|
| **Mystic** | Onboarding flow para nuevos artistas | Un artista puede registrarse solo |
| **Abraham** | Invitar a 3 artistas a la plataforma | 3 artistas registrados |
| **Juntos** | Verificar que ven sus datos correctamente | NPS de artistas |

### Martes — Revenue
| Quién | Actividad | Entregable |
|-------|-----------|------------|
| **Mystic** | Revenue split automático, generación de reportes | Reporte de revenue semanal automático |
| **Abraham** | Configurar payout splits por artista | Splits personalizados por artista |
| **Juntos** | Verificar que los cálculos son correctos | Precisión 100% en splits |

### Miércoles — Contenido Automático
| Quién | Actividad | Entregable |
|-------|-----------|------------|
| **Mystic** | Pipeline contenido automático: canción → portada → video → redes | Todo automático desde el release |
| **Abraham** | Definir template de contenido por género | Templates listos |
| **Juntos** | Release de prueba: generar contenido completo para 1 canción | Contenido completo generado |

### Jueves — Analytics
| Quién | Actividad | Entregable |
|-------|-----------|------------|
| **Mystic** | Dashboard analítico: tendencias, predicciones, insights | Analytics dashboard |
| **Abraham** | Definir KPIs semanales para cada artista | KPIs personalizados |
| **Juntos** | Ver reporte semanal generado automáticamente | Reporte funcionando |

### Viernes — Release v2.0
| Quién | Actividad | Entregable |
|-------|-----------|------------|
| **Mystic** | Sandbox, fixes, deploy | Release v2.0 |
| **Abraham** | Feedback de artistas, priorizar mejoras | Roadmap v3.0 |
| **Juntos** | Review, ajustar para semana 3 | Semana 2 completada |

---

## Semana 3: Expansión

### Lunes — Multi-Artist
| Quién | Actividad | Entregable |
|-------|-----------|------------|
| **Mystic** | Multi-tenant: cada artista ve solo sus datos | Aislamiento por artista |
| **Abraham** | Onboarding masivo: invitar a 10 artistas | 10 artistas en plataforma |
| **Juntos** | Verificar aislamiento de datos | Seguridad OK |

### Martes — Distribución
| Quién | Actividad | Entregable |
|-------|-----------|------------|
| **Mystic** | Integración con distribuidoras (DistroKid, TuneCore) | Subir releases desde ABE |
| **Abraham** | Configurar cuentas de distribución | Cuentas listas |
| **Juntos** | Primer release distribuido desde ABE | Release en Spotify via ABE |

### Miércoles — Fan CRM
| Quién | Actividad | Entregable |
|-------|-----------|------------|
| **Mystic** | CRM de fans: tracking, segmentación, comunicación | Fan CRM funcionando |
| **Abraham** | Importar base de fans actual | Fanbase en el sistema |
| **Juntos** | Primera campaña de email a fans | Campaña enviada |

### Jueves — Monetización
| Quién | Actividad | Entregable |
|-------|-----------|------------|
| **Mystic** | Tienda de merch integrada con Printful | Store funcionando |
| **Abraham** | Definir productos de merch por artista | Productos listos |
| **Juntos** | Primer merch vendido desde ABE | Venta real |

### Viernes — Release v3.0
| Quién | Actividad | Entregable |
|-------|-----------|------------|
| **Mystic** | Release completo, documentación | Release v3.0 + docs |
| **Abraham** | Plan de crecimiento mensual | Roadmap Q3 |
| **Juntos** | Cierre del sprint, celebración | 🎉 |

---

## Métricas de Progreso

| Métrica | Semana 1 | Semana 2 | Semana 3 |
|---------|----------|----------|----------|
| Artistas en plataforma | 3 → 5 | 5 → 10 | 10 → 20 |
| Tools funcionando | 166 | 180 | 200 |
| Workflows automáticos | 3 | 6 | 10 |
| Tests | 553 | 600 | 700 |
| Revenue trackeado | Manual | Automático | Predictivo |
| Contenido generado | 0 | 10 piezas | 50 piezas |

---

## Stack Diario

```bash
# Cada día empezar con:
ssh ubuntu@149.56.46.173          # Conectar al VPS
curl http://127.0.0.1:18989/api/health  # Verificar gateway
node tests/mcp/test-gateway.js    # Tests gateway
node tests/mcp/test-agents.js     # Tests agents
sdc workflow list                 # Ver workflows
sdc agent list                    # Ver agents
```

**Regla de oro**: Antes de terminar el día, todo lo que funciona hoy debe seguir funcionando mañana → correr sandbox antes de irse.
