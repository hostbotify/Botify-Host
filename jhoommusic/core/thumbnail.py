import asyncio
import hashlib
import logging
from io import BytesIO
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import requests

from .bot import app
from ..utils.cache import get_cached_data, set_cached_data
from ..utils.helpers import format_duration

logger = logging.getLogger(__name__)

async def generate_thumbnail(
    title: str,
    artist: str = "Unknown Artist",
    duration: int = 0,
    cover_url: str = None,
    requester_id: int = None,
    progress: float = 0.0
) -> BytesIO:
    """Generate advanced music thumbnail"""
    try:
        # Check cache
        cache_key = f"thumb_{hashlib.md5(title.encode()).hexdigest()}"
        cached_thumb = await get_cached_data(cache_key)
        if cached_thumb:
            return BytesIO(cached_thumb)

        # Create base image
        img = Image.new("RGB", (800, 600), (0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Gradient background
        for y in range(600):
            r = int(20 + y * 0.1)
            g = int(20 + y * 0.05)
            b = int(30 + y * 0.07)
            draw.line([(0, y), (800, y)], fill=(r, g, b))

        # Load fonts (fallback for Linux)
        try:
            font_title = ImageFont.truetype("arial.ttf", 36)
            font_artist = ImageFont.truetype("arial.ttf", 28)
            font_info = ImageFont.truetype("arial.ttf", 24)
        except:
            try:
                font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
                font_artist = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
                font_info = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
            except:
                font_title = font_artist = font_info = ImageFont.load_default()

        # Album cover
        if cover_url:
            try:
                response = await asyncio.get_event_loop().run_in_executor(
                    None, lambda: requests.get(cover_url, timeout=5)
                )
                cover_img = Image.open(BytesIO(response.content)).convert("RGB")
                cover_img = cover_img.resize((300, 300), Image.LANCZOS)

                border_img = Image.new('RGB', (304, 304), (255, 255, 255))
                border_img.paste(cover_img, (2, 2))
                img.paste(border_img, (50, 150))
            except Exception as e:
                logger.warning(f"Cover image error: {e}")

        # Shadowed text
        def draw_text_with_shadow(x, y, text, font, fill, shadow=(0, 0, 0)):
            draw.text((x+2, y+2), text, font=font, fill=shadow)
            draw.text((x, y), text, font=font, fill=fill)

        # Truncate helper
        def truncate(text, max_len):
            return text[:max_len] + "..." if len(text) > max_len else text

        # Add texts
        draw_text_with_shadow(400, 200, truncate(title, 30), font_title, (255, 255, 255))
        draw_text_with_shadow(400, 250, f"by {truncate(artist, 25)}", font_artist, (200, 200, 200))
        draw_text_with_shadow(400, 300, f"Duration: {format_duration(duration)}", font_info, (150, 150, 150))
        draw_text_with_shadow(400, 330, f"Time: {datetime.now().strftime('%H:%M')}", font_info, (150, 150, 150))

        # Progress bar
        if progress > 0:
            bar_width = 300
            progress_width = int(bar_width * progress)
            draw.rectangle([400, 380, 400 + bar_width, 390], fill=(50, 50, 50))
            draw.rectangle([400, 380, 400 + progress_width, 390], fill=(0, 255, 0))

        # Requester
        if requester_id:
            try:
                user = await app.get_users(requester_id)
                draw_text_with_shadow(400, 420, f"Requested by: {user.first_name}", font_info, (100, 100, 255))
            except Exception:
                pass

        # Branding
        draw_text_with_shadow(50, 550, "JhoomMusic Bot", font_info, (255, 255, 255))

        # Save to BytesIO
        thumb = BytesIO()
        img.save(thumb, "JPEG", quality=95)
        thumb.seek(0)

        # Cache result
        await set_cached_data(cache_key, thumb.getvalue())
        return thumb

    except Exception as e:
        logger.error(f"Thumbnail generation error: {e}")
        fallback = Image.new("RGB", (800, 600), (50, 50, 50))
        draw = ImageDraw.Draw(fallback)
        draw.text((100, 300), truncate(title, 50), fill=(255, 255, 255))
        thumb = BytesIO()
        fallback.save(thumb, "JPEG")
        thumb.seek(0)
        logger.warning("Returned fallback thumbnail.")
        return thumb
