"""
Data models for BPP Supershow Overlay
"""
from dataclasses import dataclass, field
from typing import Optional, List
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
    rules_text: Optional[str] = None
    errata_text: Optional[str] = None
    is_banned: bool = False
    release_set: Optional[str] = None
    srg_url: Optional[str] = None
    srgpc_url: Optional[str] = None
    comments: Optional[str] = None
    tags: List[str] = field(default_factory=list)

    # Competitor-specific fields
    power: Optional[int] = None
    agility: Optional[int] = None
    strike: Optional[int] = None
    submission: Optional[int] = None
    grapple: Optional[int] = None
    technique: Optional[int] = None
    division: Optional[str] = None
    gender: Optional[str] = None

    # MainDeckCard-specific fields
    deck_card_number: Optional[int] = None
    atk_type: Optional[AttackType] = None
    play_order: Optional[PlayOrder] = None


@dataclass
class PlayerState:
    """State for a single player"""
    player_id: int  # 1 or 2
    competitor_uuid: Optional[str] = None
    hand_count: int = 0
    deck_count: int = 30
    discard_pile: List[str] = field(default_factory=list)  # UUIDs
    in_play: List[str] = field(default_factory=list)  # UUIDs
    last_turn_roll: Optional[TurnRoll] = None
    turns_won: int = 0
    turns_passed: int = 0


@dataclass
class MatchState:
    """Complete match state"""
    match_id: str
    title: str
    stipulations: str
    crowd_meter: int = 0
    started_at: Optional[int] = None  # Unix timestamp
    player1: PlayerState = field(default_factory=lambda: PlayerState(player_id=1))
    player2: PlayerState = field(default_factory=lambda: PlayerState(player_id=2))


@dataclass
class MatchEvent:
    """Match event for recording"""
    event_id: str
    match_id: str
    timestamp: int  # Unix timestamp
    event_type: str
    player_id: Optional[int] = None
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
