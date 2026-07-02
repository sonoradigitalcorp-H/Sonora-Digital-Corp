# Lecciones — SPEC-20260701-007

## Lo que funciono bien

1. **Separar monitor de healer**: Mantener dos timers independientes evita que un bug en el healer paralice la deteccion.
2. **Telegram directo**: No pasar por n8n fue la decision correcta — si n8n esta caido, el healer aun puede notificar.
3. **Dedup por cooldown**: Simple y efectivo. No necesita estado compartido entre ejecuciones.

## Lo que no funciono

1. **Mock de Path en tests**: Mockear `Path` rompe Python internamente. Solucion: mockear `Path.exists` y `Path.read_text` por separado en vez de todo Path.
2. **httpx import dinamico**: Importar httpx dentro de la funcion complica el mock en tests. Mejor import al inicio del modulo.

## Proxima vez

1. Importar httpx al inicio del modulo (no dentro de funciones)
2. Para mock de archivos, usar `tmp_path` fixture de pytest en vez de mockear Path
3. Agregar test de integracion que verifique el flujo completo: monitor -> events -> healer -> restart
