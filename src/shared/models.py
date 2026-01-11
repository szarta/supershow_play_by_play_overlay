"""
Data models for BPP Supershow Overlay
"""

from dataclasses import dataclass, field
from enum import Enum


# Enums
class RollType(Enum):
    """Turn roll types"""

    POWER = "Power"
    TECHNIQUE = "Technique"
    AGILITY = "Agility"


class AttackType(Enum):
    """Card attack types"""

    STRIKE = "Strike"
    GRAPPLE = "Grapple"
    SUBMISSION = "Submission"


class PlayOrder(Enum):
    """Card play order"""

    LEAD = "Lead"
    FOLLOWUP = "Followup"
    FINISH = "Finish"


class CardType(Enum):
    """Card types"""

    MAIN_DECK_CARD = "MainDeckCard"
    SINGLE_COMPETITOR_CARD = "SingleCompetitorCard"
    TORNADO_COMPETITOR_CARD = "TornadoCompetitorCard"


# Data Models
@dataclass
class TurnRoll:
    """Turn roll information"""

    roll_type: RollType
    value: int  # 1-12


@dataclass
class Card:
    """Card from database"""

    db_uuid: str
    name: str
    card_type: CardType
    rules_text: str | None = None
    errata_text: str | None = None
    is_banned: bool = False
    release_set: str | None = None
    srg_url: str | None = None
    srgpc_url: str | None = None
    comments: str | None = None
    tags: list[str] = field(default_factory=list)

    # Competitor-specific fields
    power: int | None = None
    agility: int | None = None
    strike: int | None = None
    submission: int | None = None
    grapple: int | None = None
    technique: int | None = None
    division: str | None = None
    gender: str | None = None

    # MainDeckCard-specific fields
    deck_card_number: int | None = None
    atk_type: AttackType | None = None
    play_order: PlayOrder | None = None


@dataclass
class PlayerState:
    """State for a single player"""

    player_id: int  # 1 or 2
    competitor_uuid: str | None = None
    hand_count: int = 0
    deck_count: int = 30
    discard_pile: list[str] = field(default_factory=list)  # UUIDs
    in_play: list[str] = field(default_factory=list)  # UUIDs
    last_turn_roll: TurnRoll | None = None
    turns_passed: int = 0
    finish_roll: int | None = None  # Finish roll value (1-12)
    breakout_rolls: list[int] = field(default_factory=list)  # List of breakout roll values


@dataclass
class MatchState:
    """Complete match state"""

    match_id: str
    title: str
    stipulations: str
    crowd_meter: int = 0
    started_at: int | None = None  # Unix timestamp
    player1: PlayerState = field(default_factory=lambda: PlayerState(player_id=1))
    player2: PlayerState = field(default_factory=lambda: PlayerState(player_id=2))


@dataclass
class MatchEvent:
    """Match event for recording"""

    event_id: str
    match_id: str
    timestamp: int  # Unix timestamp
    event_type: str
    player_id: int | None = None
    data: dict = field(default_factory=dict)


@dataclass
class CardsManifest:
    """Cards database manifest"""

    version: int
    filename: str
    size_bytes: int
    generated: str


@dataclass
class ImageInfo:
    """Image information in manifest"""

    hash: str  # SHA256
    path: str  # Relative path


@dataclass
class ImageManifest:
    """Images manifest"""

    version: int
    generated: str
    image_count: int
    images: dict[str, ImageInfo] = field(default_factory=dict)  # uuid -> ImageInfo
