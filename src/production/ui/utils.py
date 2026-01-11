"""
UI utility functions for production view.

Includes color helpers, image loading, crowd meter rendering, and roll formatting.
"""

import logging
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageTk

from ...shared.config import Config
from ...shared.models import AttackType, RollType, TurnRoll

logger = logging.getLogger(__name__)

# Image cache: {(uuid, size): PhotoImage}
_image_cache: dict[tuple[str, tuple[int, int]], ImageTk.PhotoImage] = {}


def get_roll_color(roll_type: RollType, config: Config) -> str:
    """
    Get color for roll type from config.

    Args:
        roll_type: Roll type (POWER, TECHNIQUE, AGILITY)
        config: Configuration with color settings

    Returns:
        Color hex string (e.g., '#ff4444')
    """
    if roll_type == RollType.POWER:
        return config.production_ui.power_color
    elif roll_type == RollType.TECHNIQUE:
        return config.production_ui.technique_color
    elif roll_type == RollType.AGILITY:
        return config.production_ui.agility_color
    else:
        return config.production_ui.text_color


def get_attack_color(attack_type: AttackType, config: Config) -> str:
    """
    Get color for attack type from config.

    Args:
        attack_type: Attack type (STRIKE, GRAPPLE, SUBMISSION)
        config: Configuration with color settings

    Returns:
        Color hex string (e.g., '#ffff44')
    """
    if attack_type == AttackType.STRIKE:
        return config.production_ui.strike_color
    elif attack_type == AttackType.GRAPPLE:
        return config.production_ui.grapple_color
    elif attack_type == AttackType.SUBMISSION:
        return config.production_ui.submission_color
    else:
        return config.production_ui.text_color


def load_competitor_image(
    uuid: str, size: tuple[int, int], images_path: Path
) -> ImageTk.PhotoImage | None:
    """
    Load competitor image at specified size with caching.

    Args:
        uuid: Competitor card UUID
        size: Tuple of (width, height)
        images_path: Base path to images directory

    Returns:
        PhotoImage or None if not found
    """
    cache_key = (uuid, size)

    # Check cache
    if cache_key in _image_cache:
        return _image_cache[cache_key]

    # Load image
    first_2 = uuid[:2]
    img_path = images_path / first_2 / f"{uuid}.webp"

    if img_path.exists():
        try:
            img = Image.open(img_path)
            img = img.resize(size, Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            _image_cache[cache_key] = photo
            return photo
        except Exception as e:
            logger.error(f"Error loading image {uuid}: {e}")
            # Fall through to placeholder

    # Return placeholder
    placeholder = create_placeholder_image(size, "No Image")
    _image_cache[cache_key] = placeholder
    return placeholder


def load_card_thumbnail(
    uuid: str, images_path: Path, thumbnail_size: tuple[int, int]
) -> ImageTk.PhotoImage | None:
    """
    Load card thumbnail with caching.

    Args:
        uuid: Card UUID
        images_path: Base path to images directory
        thumbnail_size: Tuple of (width, height)

    Returns:
        PhotoImage or None if not found
    """
    return load_competitor_image(uuid, thumbnail_size, images_path)


def create_placeholder_image(size: tuple[int, int], text: str = "No Image") -> ImageTk.PhotoImage:
    """
    Create a gray placeholder image with text.

    Args:
        size: Tuple of (width, height)
        text: Text to display on placeholder

    Returns:
        PhotoImage placeholder
    """
    img = Image.new("RGB", size, color="#404040")
    draw = ImageDraw.Draw(img)

    # Try to use a font, fall back to default
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
    except Exception:
        font = ImageFont.load_default()

    # Calculate text position (centered)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (size[0] - text_width) // 2
    y = (size[1] - text_height) // 2

    draw.text((x, y), text, fill="#808080", font=font)

    return ImageTk.PhotoImage(img)


def render_crowd_meter(value: int, max_value: int = 10) -> str:
    """
    Render crowd meter as string of filled/empty circles.

    Args:
        value: Current crowd meter value
        max_value: Maximum crowd meter value (default 10)

    Returns:
        String like '●●●○○○○○○○' for value=3
    """
    filled = "●" * value
    empty = "○" * (max_value - value)
    return filled + empty


def format_roll_display(roll: TurnRoll | None) -> tuple[str, str]:
    """
    Format roll for display.

    Args:
        roll: TurnRoll or None

    Returns:
        Tuple of (type_text, value_text): ('POW', '8') or ('', '')
    """
    if not roll:
        return ("", "")

    # Get short type name
    type_map = {
        RollType.POWER: "POW",
        RollType.TECHNIQUE: "TECH",
        RollType.AGILITY: "AGI",
    }

    type_text = type_map.get(roll.roll_type, "")
    value_text = str(roll.value)

    return (type_text, value_text)


def format_finish_roll(value: int | None) -> str:
    """
    Format finish roll for display.

    Args:
        value: Finish roll value or None

    Returns:
        String like 'Finish:12' or empty string
    """
    if value is not None:
        return f"Finish:{value}"
    return ""


def format_breakout_rolls(rolls: list[int]) -> str:
    """
    Format breakout rolls for display.

    Args:
        rolls: List of breakout roll values

    Returns:
        String like 'BO:10,9,11' or empty string
    """
    if rolls:
        rolls_str = ",".join(str(r) for r in rolls)
        return f"BO:{rolls_str}"
    return ""
