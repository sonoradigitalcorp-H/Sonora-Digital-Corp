# Meta Ads Setup Guide

## 1. Crear App en Meta for Developers
1. Ve a https://developers.facebook.com/
2. Create App → Business
3. Copiar App ID y App Secret

## 2. Obtener Access Token
```bash
# En Facebook Graph API Explorer:
# https://developers.facebook.com/tools/explorer/
# Permisos necesarios: ads_management, leads_retrieval, pages_read_engagement
```

## 3. Configurar en VPS
```bash
ssh ovh
cat > ~/sonora-digital-corp/state/social/meta_ads.json << 'EOF'
{
  "access_token": "EAA...",
  "ad_account_id": "123456789",
  "page_id": "123456789",
  "form_id": "123456789"
}
EOF
```

## 4. Probar
```bash
cd ~/sonora-digital-corp && python3 products/social/meta_ads.py status
cd ~/sonora-digital-corp && python3 products/social/meta_ads.py leads
cd ~/sonora-digital-corp && python3 products/social/meta_ads.py sync
```

## 5. Crear Campaña
```bash
python3 products/social/meta_ads.py campaign --budget 500 --niche ecommerce --name "Cyber Ene-2026"
```
