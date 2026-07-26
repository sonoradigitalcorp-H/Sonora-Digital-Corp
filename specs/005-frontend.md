---
title: Frontend — Cosmic UI
date: 2026-07-25
status: draft
author: SDC Architecture Team
version: 1.0.0
---

# Frontend — Cosmic UI con Three.js

## Visión

El frontend de Mystic OS es un **universo 3D interactivo** donde cada cliente ve su mundo. No hay dashboards planos — hay planetas, cartas flotantes, neones y partículas. Los datos viven en el espacio.

## Principios

- **Zero-click**: la UI se actualiza sola via WebSocket
- **Mobile-first**: optimizado para iPhone/Android
- **Inmersivo**: Three.js con experiencia espacial
- **En vivo**: WebSocket + Server-Sent Events para datos en tiempo real

## Componentes

### CosmicScene

Renderiza el universo 3D: estrellas de fondo, rotación orbital, iluminación dinámica.

```typescript
class CosmicScene {
    private scene: THREE.Scene;
    private camera: THREE.PerspectiveCamera;
    private renderer: THREE.WebGLRenderer;

    addPlanet(planet: PlanetCard): void;
    addStars(count: number): void;
    animate(): void;
}
```

### PlanetCard (Carta-Planeta)

Cada "planeta" es un dashboard en miniatura. Representa una métrica, un servicio o un agente.

```typescript
interface PlanetCard {
    id: string;
    title: string;
    metric: string;         // Valor actual (ej: "85%")
    trend: 'up' | 'down' | 'stable';
    color: string;          // Color neón
    radius: number;         // Tamaño del planeta
    orbitRadius: number;    // Distancia al centro
    orbitSpeed: number;     // Velocidad de rotación
    dataStream: string;     // WebSocket channel
    onClick: () => void;    // Abre detalle
}
```

### WebSocket Sync

Cada carta se suscribe a un canal WebSocket. Cuando el servidor emite datos nuevos, la carta se actualiza automáticamente.

```typescript
class WebSocketSync {
    connect(tenantId: string): void;
    subscribe(cardId: string, callback: (data: any) => void): void;
    unsubscribe(cardId: string): void;
    disconnect(): void;
}
```

### Mobile Layout

- **iPhone/Android**: vista simplificada, planetas más pequeños, grid 2×2
- **Tablet**: grid 3×3 con planetas medianos
- **Desktop**: universo completo con órbitas, zoom y rotación libre

### Micro-frontends

Cada carta es independiente. Puede mostrar:

- Métricas de sistema (CPU, RAM, disco)
- Estado de agentes (online/offline/error)
- Últimas notificaciones
- Estadísticas del negocio
- Chat en vivo
- Calendario / reservas

## Stack

| Librería | Propósito |
|----------|-----------|
| Three.js | Renderizado 3D |
| React + Three Fiber | UI components |
| Socket.io / WebSocket | Tiempo real |
| TypeScript | Tipado |
| Vite | Build tool |
| TailwindCSS | Estilos 2D superpuestos |

## Flujo de Conexión

```
1. Usuario abre my.mystic.ai/{tenant}
2. Frontend carga identity desde localStorage
3. CosmicScene renderiza el universo del tenant
4. WebSocket se conecta a ws://api.mystic.ai/ws/{tenant_id}
5. Cada carta se suscribe a su canal
6. Servidor empuja datos → carta se actualiza → sin refresco
```
