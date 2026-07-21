import fal_client
import logging
from typing import Optional

logger = logging.getLogger(__name__)

LORA_TRAINER = "fal-ai/krea-2-trainer"
LORA_INFERENCE = "fal-ai/krea-2/turbo/lora"

def train_lora(
    image_urls: list[str],
    trigger_word: str = "person",
    name: Optional[str] = None,
) -> dict:
    logger.info(f"Training LoRA with {len(image_urls)} images, trigger: '{trigger_word}'")

    result = fal_client.subscribe(LORA_TRAINER, arguments={
        "images_data": [{"image_url": url} for url in image_urls],
        "trigger_word": trigger_word,
        "creator_name": name or "clon-digital",
    })

    lora_url = result.get("lora_url", "")
    lora_id = result.get("id", "")

    cost = 1.00
    logger.info(f"LoRA trained: {lora_id} (${cost})")

    return {
        "lora_id": lora_id,
        "lora_url": lora_url,
        "cost": cost,
        "trigger_word": trigger_word,
    }

def generate_with_lora(
    prompt: str,
    lora_url: str,
    trigger_word: str = "person",
    num_images: int = 1,
) -> dict:
    logger.info(f"Generating image with LoRA: {lora_url}")

    arguments = {
        "prompt": f"{trigger_word} {prompt}",
        "lora_url": lora_url,
        "num_images": num_images,
    }

    result = fal_client.subscribe(LORA_INFERENCE, arguments=arguments)

    images = []
    for img in result.get("images", []):
        images.append({
            "url": img.get("url", ""),
            "width": img.get("width", 0),
            "height": img.get("height", 0),
        })

    cost = 0.05
    return {
        "images": images,
        "cost": cost,
    }
