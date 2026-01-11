"""
State manager for production view.

Maintains local MatchState and notifies UI of changes.
"""

import logging
from collections.abc import Callable

from ..shared.database import DatabaseService
from ..shared.models import Card, MatchState, PlayerState, RollType, TurnRoll

logger = logging.getLogger(__name__)


class ProductionStateManager:
    """Manages match state for production view."""

    def __init__(self, database: DatabaseService):
        """
        Initialize state manager.

        Args:
            database: Database service for loading card data
        """
        self.db = database
        self.match_state = MatchState(
            match_id="", title="", stipulations="", crowd_meter=0, started_at=None
        )
        self.ui_callback: Callable[[str, dict], None] | None = None

    def set_ui_callback(self, callback: Callable[[str, dict], None]) -> None:
        """
        Set callback for UI updates.

        Args:
            callback: Function to call with (update_type, data)
        """
        self.ui_callback = callback

    def _get_player(self, player_id: int) -> PlayerState:
        """Get player state by ID."""
        return self.match_state.player1 if player_id == 1 else self.match_state.player2

    def _notify_ui(self, update_type: str, data: dict) -> None:
        """Notify UI of state change."""
        if self.ui_callback:
            try:
                self.ui_callback(update_type, data)
            except Exception as e:
                logger.error(f"Error in UI callback for {update_type}: {e}", exc_info=True)

    # ==================== Match State Updates ====================

    def update_match_init(self, payload: dict) -> None:
        """
        Handle match initialization.

        Args:
            payload: Match init data with match_id, title, stipulations, etc.
        """
        logger.info(f"Match init: {payload}")

        self.match_state.match_id = payload.get("match_id", "")
        self.match_state.title = payload.get("title", "")
        self.match_state.stipulations = payload.get("stipulations", "")
        self.match_state.started_at = payload.get("started_at")

        # Set competitors
        p1_uuid = payload.get("player1_competitor")
        p2_uuid = payload.get("player2_competitor")

        if p1_uuid:
            self.update_player_competitor(1, p1_uuid)
        if p2_uuid:
            self.update_player_competitor(2, p2_uuid)

        # Notify UI of full match info
        self._notify_ui(
            "match_init",
            {
                "match_id": self.match_state.match_id,
                "title": self.match_state.title,
                "stipulations": self.match_state.stipulations,
                "crowd_meter": self.match_state.crowd_meter,
            },
        )

    def update_match_reset(self) -> None:
        """Handle match reset signal."""
        logger.info("Match reset")

        # Reset state
        self.match_state = MatchState(
            match_id="", title="", stipulations="", crowd_meter=0, started_at=None
        )

        self._notify_ui("match_reset", {})

    def update_match_title(self, title: str) -> None:
        """Update match title."""
        self.match_state.title = title
        self._notify_ui("match_title", {"title": title})

    def update_match_stipulations(self, stipulations: str) -> None:
        """Update match stipulations."""
        self.match_state.stipulations = stipulations
        self._notify_ui("match_stipulations", {"stipulations": stipulations})

    def update_crowd_meter(self, value: int) -> None:
        """Update crowd meter value."""
        self.match_state.crowd_meter = value
        self._notify_ui("crowd_meter", {"value": value})

    # ==================== Player State Updates ====================

    def update_player_competitor(self, player_id: int, uuid: str) -> None:
        """
        Update player competitor and load card from database.

        Args:
            player_id: Player ID (1 or 2)
            uuid: Competitor card UUID
        """
        player = self._get_player(player_id)
        player.competitor_uuid = uuid

        # Load competitor card from database
        competitor_card = None
        if uuid:
            try:
                competitor_card = self.db.get_card_by_uuid(uuid)
                if competitor_card:
                    logger.info(f"Loaded competitor for player {player_id}: {competitor_card.name}")
                else:
                    logger.warning(f"Competitor card not found: {uuid}")
            except Exception as e:
                logger.error(f"Error loading competitor {uuid}: {e}")

        self._notify_ui(
            "player_competitor", {"player_id": player_id, "competitor_card": competitor_card}
        )

    def update_player_hand_count(self, player_id: int, count: int) -> None:
        """Update player hand count."""
        player = self._get_player(player_id)
        player.hand_count = count
        self._notify_ui("player_hand_count", {"player_id": player_id, "count": count})

    def update_player_deck_count(self, player_id: int, count: int) -> None:
        """Update player deck count."""
        player = self._get_player(player_id)
        player.deck_count = count
        self._notify_ui("player_deck_count", {"player_id": player_id, "count": count})

    def update_player_turn_roll(self, player_id: int, roll_data: dict) -> None:
        """
        Update player turn roll.

        Args:
            player_id: Player ID (1 or 2)
            roll_data: Dict with 'roll_type' and 'value'
        """
        player = self._get_player(player_id)

        # Parse roll type
        roll_type_str = roll_data.get("roll_type", "")
        try:
            roll_type = RollType(roll_type_str)
        except ValueError:
            logger.warning(f"Invalid roll type: {roll_type_str}")
            roll_type = RollType.POWER  # Default

        value = roll_data.get("value", 1)

        player.last_turn_roll = TurnRoll(roll_type=roll_type, value=value)

        self._notify_ui(
            "player_turn_roll",
            {"player_id": player_id, "roll_type": roll_type, "value": value},
        )

    def update_player_turns_passed(self, player_id: int, count: int) -> None:
        """Update player turns passed count."""
        player = self._get_player(player_id)
        player.turns_passed = count
        self._notify_ui("player_turns_passed", {"player_id": player_id, "count": count})

    def update_player_finish_roll(self, player_id: int, value: int | None) -> None:
        """Update player finish roll."""
        player = self._get_player(player_id)
        player.finish_roll = value
        self._notify_ui("player_finish_roll", {"player_id": player_id, "value": value})

    def update_player_breakout_rolls(self, player_id: int, rolls: list[int]) -> None:
        """Update player breakout rolls."""
        player = self._get_player(player_id)
        player.breakout_rolls = rolls
        self._notify_ui("player_breakout_rolls", {"player_id": player_id, "rolls": rolls})

    def update_player_discard(self, player_id: int, uuids: list[str]) -> None:
        """Update player discard pile (Phase 2)."""
        player = self._get_player(player_id)
        player.discard_pile = uuids

        # Load card objects for discard pile
        cards = []
        for uuid in uuids:
            try:
                card = self.db.get_card_by_uuid(uuid)
                if card:
                    cards.append(card)
                else:
                    logger.warning(f"Card not found in discard: {uuid}")
            except Exception as e:
                logger.error(f"Error loading discard card {uuid}: {e}")

        self._notify_ui("player_discard", {"player_id": player_id, "cards": cards})

    def update_player_in_play(self, player_id: int, uuids: list[str]) -> None:
        """Update player in-play cards (Phase 2)."""
        player = self._get_player(player_id)
        player.in_play = uuids

        # Load card objects for in-play cards
        cards = []
        for uuid in uuids:
            try:
                card = self.db.get_card_by_uuid(uuid)
                if card:
                    cards.append(card)
                else:
                    logger.warning(f"Card not found in play: {uuid}")
            except Exception as e:
                logger.error(f"Error loading in-play card {uuid}: {e}")

        self._notify_ui("player_in_play", {"player_id": player_id, "cards": cards})

    # ==================== Getters ====================

    def get_match_state(self) -> MatchState:
        """Get current match state."""
        return self.match_state

    def get_competitor(self, player_id: int) -> Card | None:
        """
        Get competitor card for player.

        Args:
            player_id: Player ID (1 or 2)

        Returns:
            Competitor Card or None
        """
        player = self._get_player(player_id)
        if player.competitor_uuid:
            try:
                return self.db.get_card_by_uuid(player.competitor_uuid)
            except Exception as e:
                logger.error(f"Error loading competitor: {e}")
        return None
