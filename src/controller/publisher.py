"""
MQTT publisher for match state updates.

This module provides high-level methods for publishing match and player state
to MQTT topics with appropriate QoS and retain settings.
"""

import logging

from ..shared.models import MatchState, TurnRoll
from ..shared.mqtt_client import MQTTClient, Topics

logger = logging.getLogger(__name__)


class MatchPublisher:
    """Publishes match state updates to MQTT broker."""

    def __init__(self, mqtt_client: MQTTClient):
        """
        Initialize the publisher.

        Args:
            mqtt_client: Connected MQTT client instance
        """
        self.mqtt = mqtt_client

    def is_connected(self) -> bool:
        """Check if MQTT client is connected."""
        return self.mqtt.connected

    def publish_match_init(self, match_state: MatchState) -> None:
        """
        Publish match initialization with all metadata.

        Args:
            match_state: Complete match state to publish
        """
        payload = {
            "match_id": match_state.match_id,
            "title": match_state.title,
            "stipulations": match_state.stipulations,
            "player1_competitor": match_state.player1.competitor_uuid,
            "player2_competitor": match_state.player2.competitor_uuid,
            "started_at": match_state.started_at,
        }
        self.mqtt.publish(Topics.MATCH_INIT, payload, qos=1, retain=True)
        logger.info(f"Published match init: {match_state.match_id}")

    def publish_match_reset(self) -> None:
        """Publish match reset signal."""
        self.mqtt.publish(Topics.MATCH_RESET, {}, qos=1, retain=True)
        logger.info("Published match reset")

    def publish_match_title(self, title: str) -> None:
        """
        Publish match title.

        Args:
            title: Match title string
        """
        self.mqtt.publish(Topics.MATCH_TITLE, title, qos=1, retain=True)
        logger.debug(f"Published match title: {title}")

    def publish_match_stipulations(self, stipulations: str) -> None:
        """
        Publish match stipulations.

        Args:
            stipulations: Stipulations string
        """
        self.mqtt.publish(Topics.MATCH_STIPULATIONS, stipulations, qos=1, retain=True)
        logger.debug(f"Published stipulations: {stipulations}")

    def publish_crowd_meter(self, value: int) -> None:
        """
        Publish crowd meter value.

        Args:
            value: Crowd meter value (0-10)
        """
        self.mqtt.publish(Topics.MATCH_CROWD_METER, value, qos=1, retain=True)
        logger.debug(f"Published crowd meter: {value}")

    def publish_player_competitor(self, player_id: int, competitor_uuid: str | None) -> None:
        """
        Publish player's competitor selection.

        Args:
            player_id: Player ID (1 or 2)
            competitor_uuid: Competitor card UUID
        """
        topic = Topics.player_topic(Topics.PLAYER_COMPETITOR, player_id)
        self.mqtt.publish(topic, competitor_uuid if competitor_uuid else "", qos=1, retain=True)
        logger.debug(f"Published player {player_id} competitor: {competitor_uuid}")

    def publish_player_hand_count(self, player_id: int, count: int) -> None:
        """
        Publish player's hand card count.

        Args:
            player_id: Player ID (1 or 2)
            count: Number of cards in hand
        """
        topic = Topics.player_topic(Topics.PLAYER_HAND_COUNT, player_id)
        self.mqtt.publish(topic, count, qos=1, retain=True)
        logger.debug(f"Published player {player_id} hand count: {count}")

    def publish_player_deck_count(self, player_id: int, count: int) -> None:
        """
        Publish player's deck card count.

        Args:
            player_id: Player ID (1 or 2)
            count: Number of cards remaining in deck
        """
        topic = Topics.player_topic(Topics.PLAYER_DECK_COUNT, player_id)
        self.mqtt.publish(topic, count, qos=1, retain=True)
        logger.debug(f"Published player {player_id} deck count: {count}")

    def publish_player_turn_roll(self, player_id: int, turn_roll: TurnRoll) -> None:
        """
        Publish player's last turn roll.

        Args:
            player_id: Player ID (1 or 2)
            turn_roll: Turn roll data (type and value)
        """
        topic = Topics.player_topic(Topics.PLAYER_TURN_ROLL, player_id)
        payload = {"roll_type": turn_roll.roll_type.value, "value": turn_roll.value}
        self.mqtt.publish(topic, payload, qos=1, retain=True)
        logger.debug(
            f"Published player {player_id} turn roll: {turn_roll.roll_type.value}={turn_roll.value}"
        )

    def publish_player_turns_passed(self, player_id: int, count: int) -> None:
        """
        Publish player's turns passed count.

        Args:
            player_id: Player ID (1 or 2)
            count: Number of turns passed
        """
        topic = Topics.player_topic(Topics.PLAYER_TURNS_PASSED, player_id)
        self.mqtt.publish(topic, count, qos=1, retain=True)
        logger.debug(f"Published player {player_id} turns passed: {count}")

    def publish_player_finish_roll(self, player_id: int, value: int | None) -> None:
        """
        Publish player's finish roll.

        Args:
            player_id: Player ID (1 or 2)
            value: Finish roll value (1-12) or None to clear
        """
        topic = Topics.player_topic(Topics.PLAYER_FINISH_ROLL, player_id)
        self.mqtt.publish(topic, value if value is not None else "", qos=1, retain=True)
        logger.debug(f"Published player {player_id} finish roll: {value}")

    def publish_player_breakout_rolls(self, player_id: int, rolls: list[int]) -> None:
        """
        Publish player's breakout rolls.

        Args:
            player_id: Player ID (1 or 2)
            rolls: List of breakout roll values
        """
        topic = Topics.player_topic(Topics.PLAYER_BREAKOUT_ROLLS, player_id)
        self.mqtt.publish(topic, rolls, qos=1, retain=True)
        logger.debug(f"Published player {player_id} breakout rolls: {rolls}")

    def publish_all_initial_state(self, match_state: MatchState) -> None:
        """
        Publish all initial match and player state.

        This should be called when starting a match to initialize all topics.

        Args:
            match_state: Complete match state
        """
        # Publish match init first
        self.publish_match_init(match_state)

        # Publish all match-level state
        self.publish_match_title(match_state.title)
        self.publish_match_stipulations(match_state.stipulations)
        self.publish_crowd_meter(match_state.crowd_meter)

        # Publish player 1 state
        self.publish_player_competitor(1, match_state.player1.competitor_uuid)
        self.publish_player_hand_count(1, match_state.player1.hand_count)
        self.publish_player_deck_count(1, match_state.player1.deck_count)
        self.publish_player_turns_passed(1, match_state.player1.turns_passed)
        self.publish_player_finish_roll(1, match_state.player1.finish_roll)
        self.publish_player_breakout_rolls(1, match_state.player1.breakout_rolls)

        # Publish player 2 state
        self.publish_player_competitor(2, match_state.player2.competitor_uuid)
        self.publish_player_hand_count(2, match_state.player2.hand_count)
        self.publish_player_deck_count(2, match_state.player2.deck_count)
        self.publish_player_turns_passed(2, match_state.player2.turns_passed)
        self.publish_player_finish_roll(2, match_state.player2.finish_roll)
        self.publish_player_breakout_rolls(2, match_state.player2.breakout_rolls)

        logger.info("Published all initial state")
