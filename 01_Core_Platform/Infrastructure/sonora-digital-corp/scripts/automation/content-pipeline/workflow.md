# Content Generation Workflow (n8n-ready)

## Pipeline
```
Trigger → Decide type → Generate → Store → Deploy
```

### 1. Product Photos
```
Trigger: New product added to catalog
  → ContentPipeline.generate_product_image(name, "studio")
  → Save to /data/generated/products/
  → Update product HTML page
  → Deploy via nginx (already served)
```

### 2. YouTube Thumbnails
```
Trigger: n8n cron (daily, before publish)
  → ContentPipeline.generate_thumbnail(title)
  → Save to /data/generated/thumbnails/
  → Attach to video publish
```

### 3. Social Media Content
```
Trigger: n8n cron (3x week)
  → ContentPipeline.generate_social_post(brand, theme)
  → Save to /data/generated/social/
  → Post to Instagram/TikTok
```

## Integration
- **fal.ai**: Image generation engine
- **Local storage**: /data/generated/
- **nginx**: Serves static files
- **n8n**: Orchestrates triggers and publishing
- **Neo4j**: Logs generation metadata

## Commands
```bash
# Generate product image
python3 generator.py --product "Gorra AzREC" --style lifestyle

# Generate thumbnail
python3 generator.py --thumbnail "Ultimate AI Guide 2026"

# Generate social post
python3 generator.py --social "AzREC" "new collection drop"

# View log
python3 generator.py --log
```
