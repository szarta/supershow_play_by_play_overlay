"""
Match controller for state management and business logic.

This module provides the MatchController class which maintains the match state,
coordinates between UI and MQTT publisher, and manages competitor data from the database.
"""

import logging
import time

from ..shared.config import Config
from ..shared.database import DatabaseService
from ..shared.models import Card, MatchState, PlayerState, RollType, TurnRoll
from ..shared.mqtt_client import MQTTClient
from .publisher import MatchPublisher

logger = logging.getLogger(__name__)


class MatchController:
    """Controls match state and coordinates between UI and MQTT."""

    def __init__(self, config: Config, db_service: DatabaseService, mqtt_client: MQTTClient):
        """
        Initialize the controller.

        Args:
            config: Application configuration
            db_service: Database service for competitor queries
            mqtt_client: Connected MQTT client
        """
        self.config = config
        self.db = db_service
        self.mqtt = mqtt_client
        self.publisher = MatchPublisher(mqtt_client)

        # Initialize match state
        self.match_state = self._create_initial_state()

        # Competitor data cache
        self.competitors: list[Card] = []
        self.competitor_map: dict[str, Card] = {}  # name -> Card

        # Track if match has started
        self.match_started = False

    def _create_initial_state(self) -> MatchState:
        """Create initial empty match state."""
        return MatchState(
            match_id="",
            title="",
            stipulations="",
            crowd_meter=0,
            started_at=None,
            player1=PlayerState(player_id=1, deck_count=30),
            player2=PlayerState(player_id=2, deck_count=30),
        )

    def load_competitors(self) -> list[str]:
        """
        Load all competitors from database.

        Returns:
            Sorted list of competitor names

        Raises:
            Exception: If database query fails
        """
        try:
            self.competitors = self.db.get_competitors()
            self.competitor_map = {c.name: c for c in self.competitors}
            competitor_names = sorted([c.name for c in self.competitors])
            logger.info(f"Loaded {len(competitor_names)} competitors")
            return competitor_names
        except Exception as e:
            logger.error(f"Failed to load competitors: {e}")
            raise

    def get_competitor_by_name(self, name: str) -> Card | None:
        """
        Get competitor card by name.

        Args:
            name: Competitor name

        Returns:
            Card object if found, None otherwise
        """
        return self.competitor_map.get(name)

    def is_mqtt_connected(self) -> bool:
        """Check if MQTT client is connected."""
        return self.publisher.is_connected()

    def start_match(
        self,
        title: str,
        stipulations: str,
        crowd_meter: int,
        p1_competitor_uuid: str,
        p2_competitor_uuid: str,
    ) -> None:
        """
        Start a new match and publish initial state.

        Args:
            title: Match title
            stipulations: Match stipulations
            crowd_meter: Initial crowd meter value (0-10)
            p1_competitor_uuid: Player 1 competitor UUID
            p2_competitor_uuid: Player 2 competitor UUID
        """
        # Generate match ID
        self.match_state.match_id = f"match-{int(time.time())}"
        self.match_state.title = title
        self.match_state.stipulations = stipulations
        self.match_state.crowd_meter = crowd_meter
        self.match_state.started_at = int(time.time())

        # Set competitors
        self.match_state.player1.competitor_uuid = p1_competitor_uuid
        self.match_state.player2.competitor_uuid = p2_competitor_uuid

        # Reset player state to initial values
        self.match_state.player1.hand_count = 0
        self.match_state.player1.deck_count = 30
        self.match_state.player1.turns_passed = 0
        self.match_state.player1.last_turn_roll = None
        self.match_state.player1.finish_roll = None
        self.match_state.player1.breakout_rolls = []

        self.match_state.player2.hand_count = 0
        self.match_state.player2.deck_count = 30
        self.match_state.player2.turns_passed = 0
        self.match_state.player2.last_turn_roll = None
        self.match_state.player2.finish_roll = None
        self.match_state.player2.breakout_rolls = []

        # Publish all initial state to MQTT
        self.publisher.publish_all_initial_state(self.match_state)

        self.match_started = True
        logger.info(f"Match started: {self.match_state.match_id} - {title}")

    def reset_match(self) -> None:
        """Reset match to initial state and publish reset signal."""
        # Publish reset signal
        self.publisher.publish_match_reset()

        # Reset state
        self.match_state = self._create_initial_state()
        self.match_started = False

        logger.info("Match reset")

    def update_title(self, title: str) -> None:
        """
        Update match title and publish.

        Args:
            title: New match title
        """
        self.match_state.title = title
        if self.match_started:
            self.publisher.publish_match_title(title)

    def update_stipulations(self, stipulations: str) -> None:
        """
        Update match stipulations and publish.

        Args:
            stipulations: New stipulations
        """
        self.match_state.stipulations = stipulations
        if self.match_started:
            self.publisher.publish_match_stipulations(stipulations)

    def update_crowd_meter(self, value: int) -> None:
        """
        Update crowd meter and publish.

        Args:
            value: New crowd meter value (0-10)
        """
        # Clamp to valid range
        value = max(0, min(10, value))
        self.match_state.crowd_meter = value
        if self.match_started:
            self.publisher.publish_crowd_meter(value)

    def _get_player(self, player_id: int) -> PlayerState:
        """Get player state by ID."""
        if player_id == 1:
            return self.match_state.player1
        elif player_id == 2:
            return self.match_state.player2
        else:
            raise ValueError(f"Invalid player_id: {player_id}")

    def update_turn_roll(self, player_id: int, roll_type: RollType, value: int) -> None:
        """
        Update player's turn roll and publish.

        Args:
            player_id: Player ID (1 or 2)
            roll_type: Type of roll (POWER, TECHNIQUE, AGILITY)
            value: Roll value (1-12)
        """
        # Validate
        if not (1 <= value <= 12):
            logger.warning(f"Invalid roll value: {value}, clamping to 1-12")
            value = max(1, min(12, value))

        player = self._get_player(player_id)
        player.last_turn_roll = TurnRoll(roll_type=roll_type, value=value)

        if self.match_started:
            self.publisher.publish_player_turn_roll(player_id, player.last_turn_roll)

        logger.debug(f"Player {player_id} rolled {roll_type.value}={value}")

    def increment_hand_count(self, player_id: int) -> None:
        """
        Increment player's hand count and publish.

        Args:
            player_id: Player ID (1 or 2)
        """
        player = self._get_player(player_id)
        # Max hand size is 30 (entire deck)
        player.hand_count = min(player.hand_count + 1, 30)
        player.deck_count = 30 - player.hand_count

        if self.match_started:
            self.publisher.publish_player_hand_count(player_id, player.hand_count)
            self.publisher.publish_player_deck_count(player_id, player.deck_count)

    def decrement_hand_count(self, player_id: int) -> None:
        """
        Decrement player's hand count and publish.

        Args:
            player_id: Player ID (1 or 2)
        """
        player = self._get_player(player_id)
        # Min hand size is 0
        player.hand_count = max(player.hand_count - 1, 0)
        player.deck_count = 30 - player.hand_count

        if self.match_started:
            self.publisher.publish_player_hand_count(player_id, player.hand_count)
            self.publisher.publish_player_deck_count(player_id, player.deck_count)

    def update_finish_roll(self, player_id: int, value: int | None) -> None:
        """
        Update player's finish roll and publish.

        Args:
            player_id: Player ID (1 or 2)
            value: Finish roll value (1-12) or None to clear
        """
        player = self._get_player(player_id)

        if value is not None and not (1 <= value <= 12):
            logger.warning(f"Invalid finish roll value: {value}, clamping to 1-12")
            value = max(1, min(12, value))

        player.finish_roll = value

        if self.match_started:
            self.publisher.publish_player_finish_roll(player_id, value)

    def add_breakout_roll(self, player_id: int, value: int) -> None:
        """
        Add a breakout roll to player's list and publish.

        Args:
            player_id: Player ID (1 or 2)
            value: Breakout roll value (1-12)
        """
        player = self._get_player(player_id)

        if not (1 <= value <= 12):
            logger.warning(f"Invalid breakout roll value: {value}, clamping to 1-12")
            value = max(1, min(12, value))

        player.breakout_rolls.append(value)

        if self.match_started:
            self.publisher.publish_player_breakout_rolls(player_id, player.breakout_rolls)

    def clear_breakout_rolls(self, player_id: int) -> None:
        """
        Clear player's breakout rolls and publish.

        Args:
            player_id: Player ID (1 or 2)
        """
        player = self._get_player(player_id)
        player.breakout_rolls = []

        if self.match_started:
            self.publisher.publish_player_breakout_rolls(player_id, player.breakout_rolls)

    def increment_turns_passed(self, player_id: int) -> None:
        """
        Increment player's turns passed count and publish.

        Args:
            player_id: Player ID (1 or 2)
        """
        player = self._get_player(player_id)
        player.turns_passed += 1

        if self.match_started:
            self.publisher.publish_player_turns_passed(player_id, player.turns_passed)

    def get_player_state(self, player_id: int) -> PlayerState:
        """
        Get current player state.

        Args:
            player_id: Player ID (1 or 2)

        Returns:
            PlayerState object
        """
        return self._get_player(player_id)

    def get_match_state(self) -> MatchState:
        """
        Get current match state.

        Returns:
            MatchState object
        """
        return self.match_state
