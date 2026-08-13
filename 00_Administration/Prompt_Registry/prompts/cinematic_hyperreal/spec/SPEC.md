# SPEC — cinematic_hyperreal v1.0.0
**Fecha:** 2026-08-13 · **Estado:** test · **Dominio:** imagen/video IA de marca

## Objetivo
Generar imágenes cinematográficas e hiperrealistas para contenido de marca de Sonora Digital Corp
(agentes IA para PyMEs de Sonora) con control total de guion visual: encuadre, luz, composición y mood.

## Público
PyMEs de Sonora (dental, restaurantes, moda, bienes raíces) + creadores de contenido IA.
Plataforma: Instagram 9:16 (reels/feed), carruseles, portadas.

## Motor
- **Imagen:** FAL `fal-ai/flux/dev` (~$0.05/op) o Stable Diffusion (SDXL vía API remota si se necesita).
- **Video:** FAL `fal-ai/ltx-video` (~$0.10/op, num_frames<=64) o kling (~$0.30/op).

## Directivas de composición (todas OBLIGATORIAS)
1. Luz dorada de atardecer (golden hour) o estudio editorial dramático con rim light.
2. Profundidad de campo reducida (shallow depth of field, f/1.8).
3. Encuadre cinematográfico: regla de tercios, 35mm, aspecto editorial.
4. Textura realista: piel con poros, tela con grano, sin plastificado.
5. Color grading: tonos cálidos + acento azul/dorado de marca SDC.
6. Sin texto ilegible dentro de la imagen (texto se añade después en edición).
7. Un solo sujeto principal enfocado; fondo desenfocado con contexto del nicho.

## Criterios de aceptación (verificables)
- CA1: La imagen tiene luz dorada o rim light visible en el sujeto.
- CA2: El fondo muestra contexto del nicho (consultorio, cocina, local) desenfocado.
- CA3: El sujeto (agente IA o escena) se ve real, sin deformaciones.
- CA4: Sin texto legible dentro de la imagen.
- CA5: Costo por operación <= $0.50 (flux $0.05, ltx $0.10, kling $0.30).
- CA6: Resolución adecuada para IG (1080x1920 o 1080x1080).

## Restricciones de costo (heredadas del motor de contenido)
- num_images <= 1, num_frames <= 64, 1 generación por operación, NUNCA re-generar sin aprobación.
