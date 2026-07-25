# AzREC — Shopify Setup Guide

## 1. Crear Cuenta Shopify
1. Ve a https://shopify.com y crea cuenta
2. Usa correo de AzREC (ej. hola@azrec.mx)
3. Plan Basic ($39 USD/mes) — suficiente para empezar
4. Moneda: MXN
5. Pais: Mexico

## 2. Configurar Tienda
### Informacion Basica
- Nombre: AzREC
- Tagline: "De la A a la Z · Hermosillo, Sonora"
- Direccion: Hermosillo, Sonora, Mexico
- Email: hola@azrec.mx

### Dominio Personalizado
- Compra azrec.mx o azrec.com.mx en shopify (~$15 USD/año)
- O usa azrec.sonoradigitalcorp.com como subdominio

### Pago
- Shopify Payments (si disponible en MX)
- Mercado Pago (recomendado para Mexico)
- PayPal (alternativa)

### Envio
- Envio local Hermosillo: $50 MXN
- Envio nacional: $150 MXN
- Recogida en casa-estudio (gratis)

## 3. Productos Iniciales

### Gorras (Caps)
| Producto | Precio | SKU | Descripcion |
|----------|--------|-----|-------------|
| Gorra AzREC Classic | $399 | AZ-CAP-001 | Negra, logo bordado frontal, ajustable |
| Gorra Sonora Sunset | $449 | AZ-CAP-002 | Naranja quemado, "Sonora" en dorado |
| Gorra Desert Night | $449 | AZ-CAP-003 | Azul noche, logo reflectivo |
| Gorra Edicion Limitada | $599 | AZ-CAP-004 | Colaboracion especial, serie numerada |

### Playeras (T-Shirts)
| Producto | Precio | SKU | Descripcion |
|----------|--------|-----|-------------|
| Playera AzREC Classic | $349 | AZ-TEE-001 | Algodon 100%, logo frontal, S-3XL |
| Playera "Desierto" | $399 | AZ-TEE-002 | Diseno de espalda completo |
| Hoodie AzREC | $699 | AZ-HOOD-001 | Algodon peluche, bolsillo canguro |

### Accesorios
| Producto | Precio | SKU | Descripcion |
|----------|--------|-----|-------------|
| Tote Bag "Desierto" | $249 | AZ-ACC-001 | Lona gruesa, diseno exclusivo |
| Stickers Pack (5) | $99 | AZ-ACC-002 | Vinil, 10x10cm |
| Gorro Invierno | $349 | AZ-ACC-003 | Tejido, logo bordado |

## 4. Fotos de Producto
Las fotos reales de productos existentes se deben subir a:
- `/home/mystic/products/azrec/shopify/photos/`
- Formato: 2048x2048px, JPG/PNG
- Naming: `{sku}-{angle}.jpg` (ej. AZ-CAP-001-front.jpg)

### Sin fotos reales aun? Opciones:
1. **Mockups generados**: usar Canva o Placeit.net para mockups
2. **Fotos con celular**: fondo blanco, luz natural, 4 angulos
3. **Subir ahora**: usa la seccion de productos de Shopify admin

## 5. Apps Recomendadas
- **Oberlo / Spocket** — si quieres print-on-demand
- **Loox** — reviews de productos
- **Mailchimp** — email marketing
- **Ultimate Sales Boost** — upsells
- **Free Shipping Bar** — barra de envio gratis

## 6. Integracion con Telegram
El bot de AzREC en Telegram apunta a la tienda Shopify asi:
```
/producto:Gorra AzREC Classic
  → Enlace: https://azrec.mx/products/gorra-azrec-classic
  → Precio: $399 MXN
  → Descripcion: ...

/catalogo
  → Embed del feed de productos

/comprar [producto]
  → Link directo al checkout
```

Configurar en: `/home/mystic/products/azrec/telegram/config.json`
