"""
Content Generation Pipeline — Sonora Digital Corp
fal.ai + local storage + n8n
Generates: product images, thumbnails, social media visuals
"""
import os, json, time, urllib.request, sys
from typing import Optional, List

sys.path.insert(0, '/home/mystic/.openclaw/workspace/skills/fal-ai')
from fal_api import FalAPI

OUTPUT_DIR = "/home/mystic/sonora-digital-corp/data/generated"
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(f"{OUTPUT_DIR}/products", exist_ok=True)
os.makedirs(f"{OUTPUT_DIR}/social", exist_ok=True)
os.makedirs(f"{OUTPUT_DIR}/thumbnails", exist_ok=True)

class ContentPipeline:
    def __init__(self):
        self.api = FalAPI()
        self.image_log = f"{OUTPUT_DIR}/image_log.json"
        self._load_log()
    
    def _load_log(self):
        if os.path.exists(self.image_log):
            with open(self.image_log) as f:
                self.log = json.load(f)
        else:
            self.log = {"generations": [], "total": 0}
    
    def _save_log(self):
        with open(self.image_log, "w") as f:
            json.dump(self.log, f, indent=2)
    
    def generate_product_image(self, product_name: str, style: str = "studio") -> str:
        """Generate studio product photo"""
        prompts = {
            "studio": f"Ultrarealistic cinematic product photography of {product_name}, studio lighting on white background, detailed texture, 8k quality, commercial product shot, soft shadows, edge lighting",
            "lifestyle": f"Ultrarealistic lifestyle shot of {product_name} being worn/used, natural outdoor lighting, Sonoran desert background, warm golden hour, cinematic atmosphere, 8k quality",
            "detail": f"Ultra close-up macro shot of {product_name} showing fabric texture and details, studio lighting, shallow depth of field, 8k quality, commercial product detail",
        }
        prompt = prompts.get(style, prompts["studio"])
        
        print(f"🎨 Generating {product_name} ({style})...")
        urls = self.api.generate_and_wait(prompt=prompt, model="flux-schnell", image_size="square")
        
        if urls:
            filename = f"{product_name.replace(' ', '_').lower()}_{style}.jpg"
            path = f"{OUTPUT_DIR}/products/{filename}"
            urllib.request.urlretrieve(urls[0], path)
            
            entry = {
                "product": product_name,
                "style": style,
                "url": urls[0],
                "local": path,
                "model": "flux-schnell"
            }
            self.log["generations"].append(entry)
            self.log["total"] += 1
            self._save_log()
            return path
        return ""
    
    def generate_thumbnail(self, title: str, style: str = "youtube") -> str:
        """Generate YouTube/TikTok thumbnail"""
        prompts = {
            "youtube": f"YouTube thumbnail for video '{title}', bold text overlay area, high contrast, vibrant colors, clickbaity style, 16:9, 4k",
            "tiktok": f"TikTok thumbnail for '{title}', vertical 9:16, trendy aesthetic, vibrant, high energy",
        }
        prompt = prompts.get(style, prompts["youtube"])
        
        urls = self.api.generate_and_wait(prompt=prompt, model="flux-schnell", image_size="landscape_16_9")
        
        if urls:
            filename = f"thumb_{title.replace(' ', '_')[:20]}_{int(time.time())}.jpg"
            path = f"{OUTPUT_DIR}/thumbnails/{filename}"
            urllib.request.urlretrieve(urls[0], path)
            return path
        return ""
    
    def generate_social_post(self, brand: str, theme: str) -> str:
        """Generate Instagram/TikTok visual content"""
        prompt = f"Social media post for {brand}, theme: {theme}, modern aesthetic, clean design, {brand} branding visible, high quality, square format, instagram style"
        
        urls = self.api.generate_and_wait(prompt=prompt, model="flux-schnell", image_size="square")
        
        if urls:
            filename = f"{brand}_{theme}_{int(time.time())}.jpg"
            path = f"{OUTPUT_DIR}/social/{filename}"
            urllib.request.urlretrieve(urls[0], path)
            return path
        return ""

pipeline = ContentPipeline()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Content Generation Pipeline")
    parser.add_argument("--product", help="Generate product image")
    parser.add_argument("--style", default="studio", choices=["studio", "lifestyle", "detail"])
    parser.add_argument("--thumbnail", help="Generate thumbnail for title")
    parser.add_argument("--social", nargs=2, metavar=("BRAND", "THEME"), help="Generate social post")
    parser.add_argument("--log", action="store_true", help="Show generation log")
    
    args = parser.parse_args()
    
    if args.log:
        print(f"Total generations: {pipeline.log['total']}")
        for g in pipeline.log["generations"][-10:]:
            print(f"  {g['product']} ({g['style']}) → {g['local']}")
    
    if args.product:
        path = pipeline.generate_product_image(args.product, args.style)
        print(f"Output: {path}" if path else "Failed")
    
    if args.thumbnail:
        path = pipeline.generate_thumbnail(args.thumbnail)
        print(f"Output: {path}" if path else "Failed")
    
    if args.social:
        path = pipeline.generate_social_post(args.social[0], args.social[1])
        print(f"Output: {path}" if path else "Failed")
