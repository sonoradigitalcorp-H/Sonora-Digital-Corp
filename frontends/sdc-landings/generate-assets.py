#!/usr/bin/env python3
"""Batch generate all SDC images and videos via fal.ai"""
import sys, os, json, time
sys.path.insert(0, '/home/mystic/.openclaw/workspace/skills/fal-ai')
from fal_api import FalAPI

api = FalAPI()
OUT = '/home/mystic/sdc-landings/public/assets'
os.makedirs(f'{OUT}/images', exist_ok=True)
os.makedirs(f'{OUT}/videos', exist_ok=True)
MANIFEST = {}

def gen_image(name, prompt, model='flux-pro', size='landscape_16_9', **kw):
    print(f"\n=== Generating: {name} ===")
    print(f"Prompt: {prompt[:80]}...")
    try:
        urls = api.generate_and_wait(prompt=prompt, model=model, image_size=size, **kw)
        if urls:
            MANIFEST[name] = urls[0]
            print(f"✅ {name}: {urls[0]}")
            return urls[0]
        else:
            print(f"❌ {name}: no URLs returned")
            return None
    except Exception as e:
        print(f"❌ {name}: {e}")
        return None

def gen_video(name, prompt, model='wan-video', **kw):
    print(f"\n=== Generating video: {name} ===")
    print(f"Prompt: {prompt[:80]}...")
    try:
        resp = api.generate_video(prompt=prompt, model=model, **kw)
        result = api.wait_for_completion(resp, timeout=600)
        video = result.get('video', {})
        url = video.get('url') or result.get('url')
        if url:
            MANIFEST[name] = url
            print(f"✅ {name}: {url}")
            return url
        print(f"❌ {name}: result={json.dumps(result)[:200]}")
        return None
    except Exception as e:
        print(f"❌ {name}: {e}")
        return None

# ============================================================
# DIGITAL TWIN - PEOPLE & SCENES
# ============================================================

gen_image('dt-hero-female',
    'Medium shot portrait of a confident young Latina female creator/artist in her late 20s, dark curly hair, warm smile, sitting in a modern studio with neon cyan and violet ambient lighting, wearing a casual black hoodie, professional yet approachable, photorealistic, cinematic lighting, shallow depth of field, ultra detailed skin texture, natural pose, looking at camera, high fashion editorial style')

gen_image('dt-hero-male',
    'Medium shot portrait of a confident Afro-Latino male entrepreneur in his early 30s, short fade haircut, subtle beard, wearing a dark minimalist turtleneck, standing in a modern tech office with floor-to-ceiling windows at night, city lights visible, subtle cyan glow from a laptop screen on his face, photorealistic, cinematic lighting, sharp focus, professional yet warm expression, high detail skin texture')

gen_image('dt-step-upload',
    'Close up of a young person\'s hands holding a smartphone, phone screen shows a profile upload interface with a glowing cyan camera icon, dark room with neon cyan rim lighting, photorealistic, shallow depth of field, fingers detail, screen glow on hands, cinematic mood lighting, ultra realistic')

gen_image('dt-step-train',
    'Medium shot of a diverse tech professional wearing headphones, sitting at a desk with multiple monitors showing AI training interfaces and neural network visualizations in cyan and purple, blue light casting on face, modern clean workspace, plant in background, photorealistic, cinematic, warm ambient fill light')

gen_image('dt-step-deploy',
    'Wide shot of a happy person in their living room relaxing on a couch, holding a phone showing chat messages, subtle digital twin avatar glowing on the screen, warm cozy home environment, cyan accent lighting from devices, photorealistic, lifestyle photography, natural light from window, 4k detail')

gen_image('dt-feature-alwayson',
    'Close up macro shot of a smartphone notification screen, dark mode UI, showing an AI chat interface with quick response times, glowing cyan accents, human finger about to tap, depth of field blurring background, photorealistic product photography')

gen_image('dt-feature-multiplatform',
    'Flat lay composition of three modern devices: an iPhone, a MacBook, and a tablet, all showing the same AI chat interface, arranged on a dark wood desk with cyan ambient glow, one earbud visible, minimalist aesthetic, photorealistic overhead shot')

# ============================================================
# MYSTICVERSE - MODELS & ATMOSPHERE
# ============================================================

gen_image('mv-hero-female',
    'Stunning medium close-up portrait of a beautiful Afro-Latina woman with flawless skin, voluminous dark hair, wearing a sleek black satin top, dramatic violet and magenta neon lighting from the side, mysterious and confident expression, looking slightly away from camera, dark background with subtle violet particles, cinematic mood, editorial photography style, ultra realistic skin detail, soft glamour lighting')

gen_image('mv-hero-male',
    'Handsome medium shot of a fit Latino man with styled dark hair and subtle stubble, wearing a black silk button-up shirt partially open, leaning against a dark wall with violet and pink neon strip lights creating dramatic shadows, confident mysterious expression, artistic sensual mood, high contrast lighting, photorealistic editorial style, sharp focus on eyes')

gen_image('mv-creator-profile',
    'Profile/headshot style of a young attractive creator, soft violet rim lighting, looking directly at camera with a subtle knowing smile, dark blurred background with bokeh lights, professional but alluring, high fashion editorial photography, photorealistic, shallow depth of field, flawless skin texture')

gen_image('mv-ai-clone',
    'Creative double exposure style image: a beautiful person on the left side, and a glowing holographic digital version of them on the right side, violet and cyan neon lights, dark background, futuristic AI twin concept, artistic, photorealistic, cinematic')

# ============================================================
# SHOP - PRODUCTS & PEOPLE
# ============================================================

gen_image('shop-hero',
    'Wide shot of a modern stylish creator workspace: a clean desk with a MacBook showing course content, an SDC branded hoodie draped over the chair, a ceramic mug with a futuristic logo, a small plant, ambient cyan and warm tungsten lighting, minimalist aesthetic, photorealistic lifestyle photography, 4k detail')

gen_image('shop-hoodie-model',
    'Full body shot of a young person wearing a stylish black hoodie with a subtle futuristic tech logo on the chest, posing against a dark gradient background with cyan accent lighting, streetwear fashion style, confident relaxed pose, photorealistic, fashion photography, sharp detail on fabric texture')

gen_image('shop-course-instructor',
    'Professional headshot of a knowledgeable-looking tech instructor in their 30s, wearing glasses and a casual blazer, standing in front of a dark background with subtle tech patterns, warm friendly smile, approachable expert vibe, photorealistic corporate photography, professional lighting')

# ============================================================
# VIDEOS - DEMO
# ============================================================

gen_video('demo-digital-twin',
    'A cinematic shot of a smartphone screen showing an AI chat interface, a message comes in and the AI responds instantly with a glowing cyan effect, the camera slowly zooms in, smooth motion, tech demo style, dark mode UI, 4k quality')

gen_video('demo-mysticverse',
    'Artistic slow motion shot of violet neon lights moving across a dark room, creating a mysterious sensual atmosphere, camera pans slowly, cinematic haze, purple and pink lighting, high quality cinematic footage')

# ============================================================
# SAVE MANIFEST
# ============================================================
manifest_path = f'{OUT}/manifest.json'
with open(manifest_path, 'w') as f:
    json.dump(MANIFEST, f, indent=2)
print(f"\n\n=== MANIFEST saved to {manifest_path} ===")
print(json.dumps(MANIFEST, indent=2))
