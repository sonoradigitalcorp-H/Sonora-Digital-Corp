# language: es

Característica: Descontaminación y rediseño de páginas Pro Max
  Como dueño de Sonora Digital Corp
  Quiero que las páginas de mis clientes no parezcan AI y no tengan contenido cruzado
  Para que cada negocio muestre SOLO su propio contenido, profesional y coherente

  @nathaly @contaminacion
  Escenario: nathaly.html no contiene contenido de Tu Bandera
    Dado el archivo nathaly.html servido en producción
    Cuando busco palabras de adicciones ("adicciones", "12 Pasos", "tratamiento", "bandera", "fentanilo")
    Entonces el total de coincidencias es 0

  @nathaly @contabilidad
  Escenario: nathaly.html sí contiene su propio dominio (contabilidad)
    Dado el archivo nathaly.html
    Entonces contiene términos de contabilidad (contab, sat, impuestos, declaración, nathaly)

  @index @bug-js
  Escenario: index.html no tiene el bug lowerCase()
    Dado el archivo index.html
    Entonces no existe la cadena "lowerCase()" (el método correcto es toLowerCase())

  @tubandera @honestidad
  Escenario: tubandera.html no vende fotos IA como reales
    Dado el archivo tubandera.html
    Entonces el copy de fotos dice "imágenes representativas" (no "fotos reales")

  @comun @stack-voz
  Escenario: las 3 páginas conservan el stack voz idéntico
    Dado index.html, nathaly.html y tubandera.html
    Entonces cada una contiene MediaRecorder, /api/stt y speechSynthesis (o su patrón de TTS)
