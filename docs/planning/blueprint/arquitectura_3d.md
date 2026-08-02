# SONORA DIGITAL CORP - Arquitectura de Mundos Virtuales 3D

> **"El hogar del agente es su templo. Cada negocio merece el suyo."**

---

## 1. Principios de Diseno

### Minimo GPU, Maximo Impacto

La arquitectura 3D esta disenada para funcionar en navegadores sin necesidad de GPUs dedicadas. Se usa WebGL nativo a traves de Three.js con estas optimizaciones:

- **Geometria baja poligonal**: Maximo 5,000 triangulos por escena
- **Texturas comprimidas**: Basis Universal (KTX2), maximo 512x512
- **Sin ray tracing**: Iluminacion basada en sombreadores simples (Lambert + Phong)
- **LOD (Level of Detail)**: 3 niveles de detalle que cambian segun distancia de camara
- **Culling agresivo**: Solo se renderiza lo visible en el viewport
- **Instancing**: Objetos repetidos (sillas, mesas, plantas) usan instanced meshes
- **Sin sombras dinamicas**: Sombras pre-bakeadas en texturas (lightmaps)
- **60 FPS objetivo**: En dispositivos con GPU integrada (Intel HD 4000+)

### Framework: Three.js + React Three Fiber (R3F)

- **Three.js**: Motor 3D WebGL, 100% open source, 700KB gzipped
- **React Three Fiber**: Wrapper de React para Three.js, permite integracion con dashboard
- **@react-three/drei**: Componentes pre-construidos (camera controls, text, environment)
- **@react-three/postprocessing**: Efectos visuales (bloom, vignette, color correction)

### Estado del Agente en 3D

El avatar del agente dentro del mundo virtual refleja su estado real en tiempo real:

| Estado | Visual del Avatar | Animacion | Sonido Ambiente |
|--------|-----------------|-----------|----------------|
| **Dormido** (inactivo 15+ min) | Acostado en silla/sillon, ojos cerrados | Respiracion suave (sube y baja) | Sonido suave de ventilador/noche |
| **Despierto** (idle, esperando) | Sentado erguido, mirando pantalla | Parpadeo ocasional, movimiento sutil | Clicks de teclado suaves |
| **En Llamada** (activo) | De pie, gesto de hablar, mic encendido | Boca se mueve, gestos con manos | Voz del prospecto (apagada/privacidad) |
| **Procesando** (LLM thinking) | Mirando hacia arriba, indicador de carga | Pulso de luz en la cabeza | Zumbido suave de procesamiento |
| **En Reunion** (swarm) | Rodeado de otros avatares mas pequenos | Todos con movimiento coordinado | Murmullo de multiples voces |
| **Alerta** (error/critico) | Parpadeo rojo, posture de atencion | Destello de alerta intermitente | Sonido de notificacion |
| **Offline** (desconectado) | Sombra gris, semi-transparente | Ninguna | Silencio absoluto |

### Latencia del Estado 3D

El estado del agente se propaga via WebSocket con maximo 500ms de latencia entre el evento real y la actualizacion visual 3D. Se usa un sistema de interpolacion para que las transiciones de estado se vean suaves (lerp entre posiciones).

---

## 2. Escenarios por Rol de Negocio

Cada cliente ve un escenario 3D diferente segun el tipo de negocio. No es un mundo generico: es EL hogar del agente de ese negocio especifico.

### CEO / Ejecutivo

```
Escenario: Oficina ejecutiva en piso alto
- Pisos de cristal con vista a ciudad nocturna (skybox)
- Escritorio de madera oscura con 2 monitores
- Silla ejecutiva de cuero
- Estanteria con libros y plantas
- Reloj analogico en la pared
- Ventanas con luces de ciudad lejanas
Paleta: Azul oscuro (#0f172a), Oro (#c9a227), Blanco frio (#f8fafc)
```

### Contador / Despacho de Contabilidad

```
Escenario: Despacho contable profesional
- Escritorio ordenado con calculadora, archiveros
- Libros contables en estanteria
- Planta verde en rincón
- Ventana con vista a edificio de oficinas
- Reloj de pared grande
- Certificados enmarcados
Paleta: Azul corporativo (#1e3a5f), Blanco (#ffffff), Gris claro (#f1f5f9)
```

### Restaurante / Comida

```
Escenario: Seccion de un restaurante elegante
- Barra con botellas
- Mesa con cubiertos y vela
- Luz calida ambiental
- Espejos en la pared
- Menus en soportes
- Planta colgante
Paleta: Naranja calido (#f97316), Crema (#fef3c7), Madera (#92400e)
```

### Barberia / Estetica

```
Escenario: Barberia moderna vintage
- Sillon de barbero de cuero
- Espejos con iluminacion de neón
- Estanteria con productos
- Piso de azulejo blanco y negro
- Planta en maceta colgante
- Detalles de madera oscura
Paleta: Negro (#111827), Dorado (#d4a017), Blanco (#f9fafb)
```

### Clinica Dental / Salud

```
Escenario: Recepcion de clinica moderna
- Escritorio de recepcion limpio
- Sillas de espera minimalistas
- Pizarra con informacion
- Planta decorativa
- Luz blanca clinical
- Pantalla con informacion de citas
Paleta: Azul medico (#0ea5e9), Blanco puro (#ffffff), Verde suave (#d1fae5)
```

### Creador OnlyFans / NSFW

```
Escenario: Estudio creativo privado
- Iluminacion suave y calida (no fria)
- Camara en tripod
- Anillo de luz
- Pantallas de edicion
- Estanteria con accesorios
- Cortinas que dan privacidad
- Moodboard en la pared
Paleta: Rosa oscuro (#be185d), Purpura (#7c3aed), Negro suave (#1f1f1f)
NOTA: Este escenario solo se activa tras KYC NSFW aprobado.
       No tiene elementos sexuales. Es el ESTUDIO, no la escena.
```

### Agencia de Marketing

```
Escenario: Oficina creativa
- Paredes con post-its y moodboards
- Multiple monitores con dashboards
- Cafetera en rincón
- Plantas colgantes
- Libros de diseno en estanteria abierta
- Cojines en suelo
Paleta: Morado vibrante (#8b5cf6), Amarillo (#facc15), Blanco (#fafafa)
```

---

## 3. Vistas por Paquete

### Despertar (No tiene 3D)

El paquete Despertar NO incluye mundo 3D. El cliente ve:
- Dashboard 2D basico con metricas
- Lista de llamadas con transcripcion
- Graficos de actividad (barras y lineas simples)
- Indicador de estado del agente: icono con emoji (zZz para dormido, verde para activo)

### Elevar (Dashboard 2D Avanzado, sin 3D)

- Dashboard 2D con metricas en tiempo real
- Mapa de calor de llamadas
- Temperamento del prospecto (iconos de cara)
- Estado del agente con indicador visual animado (no 3D, pero con animaciones CSS)
- Transcripcion en vivo con highlight de palabras clave
- Graficos interactivos (hover para detalles)

### Soberano (Dashboard 3D JARVIS)

- Escenario 3D completo del rol del negocio
- Avatar del agente con estados animados
- HUD overlay con metricas en tiempo real
- Transiciones suaves entre estados
- Iluminacion ambiental que cambia con la actividad
- Sonido ambiente segun estado
- Posibilidad de rotar la camara (orbit controls)
- Accesible desde navegador, sin instalar nada

### Oraculo (Mundo Inmersivo + JARVIS Desktop)

- Todo de Soberano mas:
- **Interaccion por voz**: Puedes hablarle a tu agente en el mundo 3D
- **Avatar animado completo**: El avatar camina, gesticula, reacciona
- **Notificaciones ambientales**: Cuando llega un lead, una particula dorada aparece
- **JARVIS Desktop**: Aplicacion Electron que corre como widget en tu computadora
- **Vista multi-tenant**: Ves los mundos de todos tus sub-clientes en una cuadricula
- **Modo noche/dia**: El escenario cambia de iluminacion segun hora real
- **Mini-mapa**: Si tienes multiples agentes, ves una vista panoramica del "edificio" con cada agente en su "oficina"

---

## 4. Arquitectura Tecnica

```
[Navegador Cliente]
    |
    | WebSocket (wss://)
    v
[API Gateway - FastAPI]
    |
    | Pub/Sub Redis
    v
[Agent State Service]
    |  - Lee estado de cada agente desde Redis
    |  - Publica cambios via WebSocket
    |  - Interpola transiciones (lerp)
    v
[Three.js Scene - Cliente]
    |  - Recibe estado via WS
    |  - Actualiza avatar (posicion, animacion, color)
    |  - Renderiza a 60 FPS con GPU del cliente
    |  - GPU usada: minima (5-15% de GPU integrada)
```

### Tamanos de Carga

| Recurso | Tamanio | Compresion |
|---------|---------|-----------|
| Three.js + R3F bundle | 200KB | Gzipped |
| Escenario 3D (GLB) | 150-300KB | Draco compressed |
| Texturas (KTX2) | 50-100KB | Basis Universal |
| Animaciones | 20-50KB | GlTF Animation |
| **Total primera carga** | **~500KB** | **~200KB comprimido** |
| Actualizaciones WS | <1KB | Por evento |

### Cache y Lazy Loading

- Escenarios se cachean en IndexedDB despues de la primera descarga
- Animaciones se cargan solo cuando el agente cambia de estado
- Texturas se cargan progresivamente (primero baja resolucion, luego alta)
- Service Worker para funcionamiento offline del dashboard basico

---

## 5. Que Ve Cada Quien

| Elemento 3D | Mystic (Tu) | Cliente Despertar | Cliente Elevar | Cliente Soberano | Cliente Oraculo |
|------------|-------------|------------------|---------------|-----------------|----------------|
| Mundo 3D propio | Admin (todos) | No | No | Si (su rol) | Si (inmersivo) |
| Avatar de agente | Todos (47+) | Icono 2D | Animacion CSS | Avatar 3D | Avatar 3D + voz |
| Estado dormido | Indicador | zZz icon | Animacion pausa | Avatar acostado | Avatar acostado + sonido |
| Estado llamada | Lista en vivo | Texto | Texto + indicador | Avatar hablando | Avatar hablando + onda |
| HUD metricas | Admin completo | Basico | Avanzado 2D | Overlay 3D | Overlay 3D + voz |
| Multi-agente | Cuadricula admin | N/A (1 agente) | Lista 2D | Mini-mapa 3D | Edificio completo |
| Sonido ambiente | No | No | No | Si | Si + interactivo |
| Camara libre | Si (admin) | No | No | Orbit controls | Orbit + fly |

---

*Sonora Digital Corp - Los Mundos del Templo*