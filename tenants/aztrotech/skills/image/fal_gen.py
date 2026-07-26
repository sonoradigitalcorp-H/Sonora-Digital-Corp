import os
import logging

logger = logging.getLogger("aztrotech.fal")

FAL_KEY = os.environ.get("FAL_KEY")
_configured = False


def configure():
    global _configured
    if not FAL_KEY:
        logger.warning("FAL_KEY not set")
        return
    os.environ["FAL_KEY"] = FAL_KEY
    _configured = True


def _ensure():
    if not _configured:
        configure()
    if not FAL_KEY:
        raise RuntimeError("FAL_KEY not configured")


async def generate_image(prompt: str, image_url: str | None = None) -> dict:
    _ensure()
    import fal_client

    args = {
        "prompt": prompt,
        "image_size": "landscape_4_3",
        "num_images": 1,
        "guidance_scale": 3.5,
        "num_inference_steps": 28,
    }
    if image_url:
        args["control_image_url"] = image_url

    result = fal_client.run("fal-ai/flux-pro/v1.1", arguments=args)
    images = result.get("images", [])
    if images:
        return {
            "url": images[0].get("url", ""),
            "width": images[0].get("width", 0),
            "height": images[0].get("height", 0),
        }
    return {"url": "", "width": 0, "height": 0}


async def generate_character(prompt: str, reference_image_url: str) -> dict:
    _ensure()
    import fal_client

    result = fal_client.run("fal-ai/flux-pro/v1.1", arguments={
        "prompt": prompt,
        "image_size": "portrait_4_3",
        "num_images": 1,
        "guidance_scale": 3.5,
        "num_inference_steps": 28,
        "reference_image_url": reference_image_url,
        "reference_type": "identity",
    })
    images = result.get("images", [])
    if images:
        return {
            "url": images[0].get("url", ""),
            "width": images[0].get("width", 0),
            "height": images[0].get("height", 0),
        }
    return {"url": "", "width": 0, "height": 0}


async def face_swap(target_image_url: str, face_image_url: str) -> str:
    _ensure()
    import fal_client

    result = fal_client.run("fal-ai/face-swap", arguments={
        "target_image_url": target_image_url,
        "face_image_url": face_image_url,
    })
    return result.get("image", {}).get("url", "")


def list_models() -> list[str]:
    return [
        "fal-ai/flux-pro/v1.1",
        "fal-ai/face-swap",
        "fal-ai/stable-diffusion-v3-medium",
        "fal-ai/fast-sdxl",
    ]
