# LECCION — ECA Fase 1

## Qué salió bien

1. **Arquitectura cognitiva**: reorganizar apps/ en 7 niveles (observe→understand→decide→act→measure→learn→control) hizo que el sistema sea inmediatamente comprensible sin documentación externa
2. **Zero borrados**: backward-compat wrappers permitieron mover ~15 archivos sin romper ningún import existente
3. **Execution Kernel**: 24 tests, todos pasando. Cola persistente SQLite + prioridad + retry backoff cubren todos los FRs
4. **Evolution Loop**: ciclo completo measure→propose→simulate→approve→implement con dry-run
5. **Artist Intelligence**: 4 collectors con pipeline completo (raw→normalize→derive→store)
6. **Control Plane**: dashboard unificado con health + scoreboard + events + cost

## Qué falló

1. **Backward compat**: los `__init__.py` con `from X import *` no funcionan para sub-módulos. Hubo que crear `.py` individuales por cada módulo movido
2. **Test preexistente**: test_learned_is_empty no se actualizó cuando se agregaron las 9 reglas aprendidas la sesión anterior

## Qué aprender para la próxima

1. Backward compat en Python requiere archivos `.py` individuales, no `__init__.py` con import estrella
2. Los tests de truth (test_all_truth_files_exist) fallan silenciosamente cuando se agregan nuevos truth files — mantener sincronizado
3. systemctl restart sobre SSH sigue timeouteando — mejor usar kill -9 + reset-failed + start
4. 60 tests en 3 suites distintas es manejable (78 en total incluyendo ABE)
