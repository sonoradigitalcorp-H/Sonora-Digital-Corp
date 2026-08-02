---
type: decision
title: "Almacenamiento: Supabase Storage"
status: active
tags: [decision, architecture, storage]
created: 2026-07-18
---

# Almacenamiento: Supabase Storage

**Contexto**: Se necesita almacenar fotos de clientes, modelos entrenados, y assets generados.

**Decisión**: Usar Supabase Storage (bucket sdc-assets) con estructura /clients/{id}/.

**Consecuencia**: Assets expiran a 30 días. URLs públicas para el cliente.
