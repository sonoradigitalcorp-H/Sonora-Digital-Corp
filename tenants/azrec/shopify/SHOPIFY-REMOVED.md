# AzREC — Shopify REMOVED (not open source)

## Decision: Self-hosted store under sonoradigitalcorp.com

Instead of Shopify, we use:
- **Landing page** with catalog (already built in landing/index.html)
- **Static product pages** served via nginx under sonoradigitalcorp.com/azrec/
- **Telegram bot** handles orders and redirects to our own pages
- **Future:** WooCommerce (WordPress, open source) or Medusa.js if needed

## URL Structure
```
sonoradigitalcorp.com/azrec/           ← Landing page
sonoradigitalcorp.com/azrec/catalogo   ← Product catalog
sonoradigitalcorp.com/azrec/gorra-classic  ← Individual product
sonoradigitalcorp.com/azrec/playera-classic
```

## Payment
- Mercado Pago (open API, works in Mexico)
- Or handle via Telegram: customer asks bot → manual quote → OXXO/transfer

## No migration needed — we never created the Shopify store
Just update the landing page links to point to our own URLs.
