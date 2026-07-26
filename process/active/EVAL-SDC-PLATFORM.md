# Evaluación — SDC Platform (White-Label Agent Reseller)

**Versión**: 1.0  
**Fecha**: 2026-07-23  
**Especificación**: `SPEC-SDC-PLATFORM`  
**Puntaje mínimo**: 135/200 (67.5%) para aprobar  

---

## Instrucciones

Cada criterio se puntúa de 0 a 10.  
0 = no implementado / no funcional.  
5 = implementación parcial con bugs.  
10 = implementación completa, robusta, con pruebas.  

Marcar `[ ]` con el puntaje al evaluar.

---

## Categoría A: Landing Page (50 pts)

### A1. Hero y tagline
`[ ] /10` — El hero se renderiza con el tagline "El Sistema Operativo de IA para tu Negocio". Ambos CTAs ("Ver Planes" y "Comenzar") funcionan y scrolleoan/navegan correctamente. Responsive: se ve bien en 375px.  
**Prueba**: Abrir landing, verificar tagline, clickear ambos botones.

### A2. Showcase de 3 agentes
`[ ] /10` — Los 3 agentes (Voz, CRM, Social) se muestran con ícono, descripción, beneficios y CTA individual. En mobile (<768px) se apilan verticalmente. Cada CTA lleva a pricing o registro.  
**Prueba**: Verificar 3 cards visibles. Redimensionar a 375px → stack vertical.

### A3. Pricing dinámico desde YAML
`[ ] /10` — La sección pricing carga datos de `config/pricing-tiers.yaml`. Al cambiar industria (tabs o select), los precios (setup, monthly, markup, revenue share) se actualizan sin recargar. Planes Small/Medium/Enterprise visibles. Fallback si YAML no existe.  
**Prueba**: Abrir landing, cambiar a "Legal", verificar precios Premium. Borrar YAML temporalmente → verificar fallback.

### A4. Cómo funciona + Testimonios + Footer
`[ ] /10` — Sección "Cómo funciona" con 3 pasos visibles y numerados. Testimonios en carrusel funcional (auto-play o navegación manual). Footer con todos los links especificados (Productos, Precios, Docs, Blog, Login, Términos, Privacidad, Contacto).  
**Prueba**: Scroll visual. Click en dots/flechas de carrusel. Verificar 8 links en footer.

### A5. Responsive design (mobile-first)
`[ ] /10` — Toda la landing se ve correctamente en: 375px (iPhone SE), 768px (iPad), 1024px+ (desktop). Sin overflow horizontal. Pricing cards no se rompen. Hero texto legible. CTAs tocables en mobile.  
**Prueba**: Chrome DevTools device toolbar en 3 breakpoints. No scroll horizontal en ninguno.

---

## Categoría B: Auth y Sesión (40 pts)

### B1. Registro con validaciones
`[ ] /10` — Formulario de registro con campos: nombre, email, empresa, industria (select), password, confirmar password. Validaciones: email formato, password ≥8 chars, passwords coinciden. Error claro si email duplicado. Toast/snackbar en éxito.  
**Prueba**: Registrar usuario nuevo. Registrar con mismo email → error. Password muy corto → error.

### B2. Login y JWT
`[ ] /10` — Login con email+password + Google OAuth. JWT guardado en localStorage. Al navegar a ruta privada sin JWT → redirect a `#login`. Al hacer logout → JWT eliminado, redirect a landing.  
**Prueba**: Login exitoso → ver JWT en localStorage. Cerrar sesión → JWT eliminado. Acceder a `#dashboard` sin JWT → redirect.

### B3. Refresh token automático
`[ ] /10` — El sistema refresca el JWT silenciosamente antes de expirar. Si el refresh falla, reintenta 2 veces con backoff. Si todo falla, redirige a `#login` con mensaje.  
**Prueba**: Manipular JWT expirado → verificar redirect con mensaje. Forzar fallo de refresh → verificar reintentos.

### B4. Sesión multi-pestaña
`[ ] /10` — Si el usuario cierra sesión en una pestaña, las otras pestañas detectan el cambio (via `window.addEventListener('storage', ...)`) y redirigen a login sin errores.  
**Prueba**: Abrir 2 pestañas autenticadas. Cerrar sesión en pestaña A → pestaña B redirige sola.

---

## Categoría C: SPA y Navegación (30 pts)

### C1. Hash routing funcional
`[ ] /10` — Las 6 rutas funcionan: `#login`, `#dashboard`, `#catalogo`, `#mis-agentes`, `#reseller`, `#perfil`. Cada ruta carga su contenido sin recarga completa de página. El hash en URL se actualiza correctamente con botones back/forward del navegador.  
**Prueba**: Navegar todas las rutas clickeando. Usar botones back/forward del navegador. Verificar URL hash.

### C2. Carga dinámica de secciones
`[ ] /10` — Cada sección se carga via `fetch('sections/nombre.html')` y se inyecta en `<main>`. Sin contenido estático precargado de otras secciones. Tiempo de carga de sección <500ms.  
**Prueba**: Abrir network tab. Navegar secciones. Verificar fetch requests individuales.

### C3. Manejo de errores 404 y estados
`[ ] /10` — Ruta hash inválida (`#xyz`) muestra página 404 con mensaje "Sección no encontrada" y botón "Volver al Dashboard". Estados de carga (spinner) y error visibles en cada sección.  
**Prueba**: Navegar a `#invalido` → ver 404. Desconectar API → ver estado de error en dashboard.

---

## Categoría D: Dashboard y KPIs (30 pts)

### D1. KPIs del dashboard
`[ ] /10` — Dashboard muestra: agentes activos (número), revenue generado (formato moneda), clientes activos (número), últimos 7 días de actividad (gráfico de barras). Los datos vienen de MCP Gateway + PostgreSQL.  
**Prueba**: Verificar 4 KPIs visibles. Gráfico de barras con 7 columnas.

### D2. Estado offline de MCP Gateway
`[ ] /10` — Si MCP Gateway (:18989) no responde, el dashboard muestra indicador visual rojo, KPIs en "Datos no disponibles", y banner de servicio offline. Cuando el gateway se recupera, los datos vuelven automáticamente.  
**Prueba**: Detener MCP Gateway → verificar estado offline. Reactivar → verificar recuperación automática.

### D3. Integración MCP real
`[ ] /10` — Los KPIs y datos del dashboard se obtienen mediante llamadas reales a `GET /mcp/health` y `POST /mcp/execute`. Sin mock data en producción. Timeout 5s manejado.  
**Prueba**: Verificar en network tab llamadas a localhost:18989. Verificar headers y payload.

---

## Categoría E: Catálogo y Licencias (25 pts)

### E1. Catálogo de agentes
`[ ] /10` — Grid con 3 agentes mostrando nombre, descripción, precio base, y botón "Comprar licencia". Modal de compra con: selección de plan (Small/Medium/Enterprise), cantidad, markup, y resumen de costo total.  
**Prueba**: Click "Comprar licencia" → modal visible con campos. Cambiar cantidad → total se actualiza.

### E2. Mis Agentes (gestión)
`[ ] /10` — Tabla con licencias compradas: agente, tier, estado (active/inactive/pending), expiración, cliente asignado, acciones (configurar, pausar, cancelar). Estados de tabla vacía con CTA "Comprar tu primer agente".  
**Prueba**: Comprar licencia → aparece en tabla. Click pausar → estado cambia. Tabla vacía → CTA visible.

### E3. Validaciones de compra
`[ ] /5` — Markup no puede exceder máximo configurable. Cantidad mínima 1. Precio total calculado correctamente (setup + monthly * qty * markup). Confirmación antes de comprar.  
**Prueba**: Markup 12x → rechazado. Cantidad 0 → rechazado. Verificar cálculo.

---

## Categoría F: Portal Reseller (20 pts)

### F1. Lista de clientes y revenue
`[ ] /10` — Portal muestra: tabla de clientes del revendedor con nombre, email, markup aplicado, agente asignado, revenue share acumulado. Cálculo de revenue share visible por cliente.  
**Prueba**: Agregar cliente → aparece en tabla. Verificar revenue share calculado.

### F2. Agregar cliente y estado vacío
`[ ] /10` — Botón "Agregar Cliente" con formulario (nombre, email, markup personalizado). Si no hay clientes, se muestra estado vacío con CTA "Agregar primer cliente".  
**Prueba**: Portal vacío → CTA visible. Agregar cliente → formulario → cliente en tabla.

---

## Categoría G: Perfil y Ajustes (15 pts)

### G1. Editar perfil
`[ ] /10` — Formulario para editar: nombre, email (con validación), empresa. Cambio de contraseña: contraseña actual + nueva + confirmar. Toast de confirmación al guardar.  
**Prueba**: Cambiar nombre → guardar → ver reflejado. Cambiar password → login con nueva password.

### G2. Preferencias de idioma y tema
`[ ] /5` — Selector de idioma (es/en) funcional. Tema oscuro por defecto (coherente con design system). Preferencias persisten en localStorage.  
**Prueba**: Cambiar a inglés → UI en inglés. Recargar → preferencia persiste.

---

## Categoría H: Design System (15 pts)

### H1. Consistencia visual
`[ ] /10` — Colores del design system aplicados consistentemente: terracota `#c85a3e` en CTAs y acentos, dorado `#d4a34a` en highlights y badges, fondo `#120c0a` en body, surface `#1e1612` en cards. Bordes redondeados 8px. Sin fugas de color ni estilos inline rotos.  
**Prueba**: Inspeccionar CSS en todas las secciones. Verificar variables CSS en :root.

### H2. Animaciones y micro-interacciones
`[ ] /5` — Transiciones suaves en hover de botones, cards y links. Animación de entrada en secciones al navegar. Sin animaciones que afecten rendimiento (GPU-accelerated preferred).  
**Prueba**: Hover botones → transición. Navegar secciones → fade/slide in.

---

## Categoría I: Técnica (15 pts)

### I1. Sin errores en consola
`[ ] /10` — Sin errores ni warnings en consola del navegador durante navegación completa de todas las secciones. Sin peticiones HTTP fallidas (404, 500). Sin errores de CORS.  
**Prueba**: Abrir console, navegar todas las rutas. 0 errores.

### I2. Desempeño Lighthouse
`[ ] /5` — Lighthouse mobile: Performance ≥70, Accessibility ≥80, Best Practices ≥80, SEO ≥90.  
**Prueba**: Correr Lighthouse audit en landing page.

---

## Resumen

| Categoría | Puntos posibles | Puntos obtenidos |
|-----------|----------------|------------------|
| A. Landing Page | 50 | `[ ]` |
| B. Auth y Sesión | 40 | `[ ]` |
| C. SPA y Navegación | 30 | `[ ]` |
| D. Dashboard y KPIs | 30 | `[ ]` |
| E. Catálogo y Licencias | 25 | `[ ]` |
| F. Portal Reseller | 20 | `[ ]` |
| G. Perfil y Ajustes | 15 | `[ ]` |
| H. Design System | 15 | `[ ]` |
| I. Técnica | 15 | `[ ]` |
| **Total** | **240** | `[ ]` |

**Resultado**: `[ ]` APRUEBA (≥160 / 240) | `[ `]` REPRUEBA (<160)
