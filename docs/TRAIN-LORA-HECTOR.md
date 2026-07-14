# Entrenar LoRA de Hector Rubio en Google Colab

**Tiempo:** ~20-30 minutos · **Costo:** $0 (GPU T4 gratuita)

## Paso 1: Abrir el Notebook

[**Abrir en Colab**](https://colab.research.google.com/github/ostris/ai-toolkit/blob/main/notebooks/FLUX_1_dev_LoRA_Training.ipynb)

## Paso 2: Configurar GPU

Runtime → Change runtime type → **T4 GPU**

## Paso 3: Configurar parámetros

En la primera celda de configuración del notebook, buscar donde dice `trigger_word` o `instance_prompt` y poner:

```
trigger_word = "hector_rubio"
instance_prompt = "a photo of hector_rubio person"
```

Buscar donde se piden las imágenes de entrenamiento y poner:

```
ZIP_URL = "https://jibalggzudkflwzdndqz.supabase.co/storage/v1/object/public/sdc-assets/hector-rubio/training/hector_photos.zip"
```

## Paso 4: Ejecutar

Runtime → Run all (Ctrl+F9)

Esperar ~20 min mientras se entrena.

## Paso 5: Descargar LoRA

Cuando termine, el notebook generará un archivo `.safetensors`. Descargarlo a tu laptop.

## Paso 6: Pasarme el archivo

El archivo `.safetensors` pesa ~100-200MB. Pasármelo y yo:
1. Lo subo a Supabase Storage
2. Actualizo el weight_id en el sistema
3. Activo `requires_lora = true` en los productos
4. Las fotos generadas tendrán la cara de Hector consistente siempre
