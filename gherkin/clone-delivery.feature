# language: es
Funcionalidad: Entrega de assets al cliente
  Como sistema de clon publicitario
  Quiero entregar los assets generados al cliente en múltiples formatos
  Para que pueda usarlos en diferentes plataformas

  Escenario: Entregar asset en Supabase Storage
    Dado que se generó un video de 15s para el cliente
    Cuando el sistema sube el asset a Supabase Storage
    Entonces el asset se almacena en /clients/{id}/output/videos/{uuid}.mp4
    Y se genera un enlace público firmado

  Escenario: Generar enlaces públicos para el cliente
    Dado que hay assets generados para el cliente
    Cuando el cliente pide: "Pásame los links de mis fotos"
    Entonces el sistema responde con URLs públicas de Supabase
    Y los enlaces expiran en 30 días

  Escenario: Exportar multi-formato
    Dado que se generó un video en 16:9
    Cuando el cliente pide: "Quiero esto para TikTok, Instagram y YouTube"
    Entonces el sistema:
      - Convierte a 9:16 (TikTok/Reels) vía FFmpeg
      - Convierte a 1:1 (Instagram) vía FFmpeg
      - Mantiene 16:9 (YouTube) original
    Y entrega 3 enlaces públicos diferentes
