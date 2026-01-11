"""
MQTT subscriber for production view.

Subscribes to all supershow/* topics and routes messages to state manager callbacks.
"""

import logging
from collections.abc import Callable
from typing import Any

from ..shared.mqtt_client import MQTTClient, Topics

logger = logging.getLogger(__name__)


class ProductionSubscriber:
    """Subscribes to MQTT topics and routes messages to handlers."""

    def __init__(self, mqtt_client: MQTTClient):
        """
        Initialize the subscriber.

        Args:
            mqtt_client: Connected MQTT client instance
        """
        self.mqtt = mqtt_client
        self.callbacks: dict[str, Callable] = {}

    def set_callback(self, callback_name: str, callback: Callable) -> None:
        """
        Set a callback function for a specific event type.

        Args:
            callback_name: Name of the callback (e.g., 'match_init', 'player_competitor')
            callback: Callable to invoke when event occurs
        """
        self.callbacks[callback_name] = callback

    def subscribe_all(self) -> None:
        """Subscribe to all supershow topics and setup message handler."""
        # Subscribe to all supershow topics
        self.mqtt.subscribe("supershow/#", qos=1)
        logger.info("Subscribed to supershow/#")

        # Set message callback
        self.mqtt.set_on_message_callback(self._on_message)

    def _on_message(self, topic: str, payload: Any) -> None:
        """
        Route incoming MQTT messages to appropriate handlers.

        Args:
            topic: MQTT topic
            payload: Message payload (already decoded by MQTTClient)
        """
        logger.debug(f"Received message on {topic}: {payload}")

        try:
            # Match topics
            if topic == Topics.MATCH_INIT:
                self._handle_match_init(payload)
            elif topic == Topics.MATCH_RESET:
                self._handle_match_reset()
            elif topic == Topics.MATCH_TITLE:
                self._handle_match_title(payload)
            elif topic == Topics.MATCH_STIPULATIONS:
                self._handle_match_stipulations(payload)
            elif topic == Topics.MATCH_CROWD_METER:
                self._handle_crowd_meter(payload)

            # Player topics - parse player_id from topic
            elif topic.startswith("supershow/player/"):
                parts = topic.split("/")
                if len(parts) >= 4:
                    player_id = int(parts[2])
                    field = "/".join(parts[3:])

                    if field == "competitor":
                        self._handle_player_competitor(player_id, payload)
                    elif field == "hand_count":
                        self._handle_player_hand_count(player_id, payload)
                    elif field == "deck_count":
                        self._handle_player_deck_count(player_id, payload)
                    elif field == "turn_roll":
                        self._handle_player_turn_roll(player_id, payload)
                    elif field == "turns_passed":
                        self._handle_player_turns_passed(player_id, payload)
                    elif field == "finish_roll":
                        self._handle_player_finish_roll(player_id, payload)
                    elif field == "breakout_rolls":
                        self._handle_player_breakout_rolls(player_id, payload)
                    elif field == "discard":
                        self._handle_player_discard(player_id, payload)
                    elif field == "in_play":
                        self._handle_player_in_play(player_id, payload)

        except Exception as e:
            logger.error(f"Error handling message on {topic}: {e}", exc_info=True)

    # ==================== Match Handlers ====================

    def _handle_match_init(self, payload: dict) -> None:
        """Handle match initialization message."""
        callback = self.callbacks.get("match_init")
        if callback:
            callback(payload)

    def _handle_match_reset(self) -> None:
        """Handle match reset signal."""
        callback = self.callbacks.get("match_reset")
        if callback:
            callback()

    def _handle_match_title(self, title: str) -> None:
        """Handle match title update."""
        callback = self.callbacks.get("match_title")
        if callback:
            callback(title)

    def _handle_match_stipulations(self, stipulations: str) -> None:
        """Handle match stipulations update."""
        callback = self.callbacks.get("match_stipulations")
        if callback:
            callback(stipulations)

    def _handle_crowd_meter(self, value: int) -> None:
        """Handle crowd meter update."""
        callback = self.callbacks.get("crowd_meter")
        if callback:
            callback(value)

    # ==================== Player Handlers ====================

    def _handle_player_competitor(self, player_id: int, uuid: str) -> None:
        """Handle player competitor update."""
        callback = self.callbacks.get("player_competitor")
        if callback:
            callback(player_id, uuid)

    def _handle_player_hand_count(self, player_id: int, count: int) -> None:
        """Handle player hand count update."""
        callback = self.callbacks.get("player_hand_count")
        if callback:
            callback(player_id, count)

    def _handle_player_deck_count(self, player_id: int, count: int) -> None:
        """Handle player deck count update."""
        callback = self.callbacks.get("player_deck_count")
        if callback:
            callback(player_id, count)

    def _handle_player_turn_roll(self, player_id: int, roll_data: dict) -> None:
        """Handle player turn roll update."""
        callback = self.callbacks.get("player_turn_roll")
        if callback:
            callback(player_id, roll_data)

    def _handle_player_turns_passed(self, player_id: int, count: int) -> None:
        """Handle player turns passed update."""
        callback = self.callbacks.get("player_turns_passed")
        if callback:
            callback(player_id, count)

    def _handle_player_finish_roll(self, player_id: int, value: int | None) -> None:
        """Handle player finish roll update."""
        callback = self.callbacks.get("player_finish_roll")
        if callback:
            # Empty string means None
            if value == "":
                value = None
            callback(player_id, value)

    def _handle_player_breakout_rolls(self, player_id: int, rolls: list[int]) -> None:
        """Handle player breakout rolls update."""
        callback = self.callbacks.get("player_breakout_rolls")
        if callback:
            callback(player_id, rolls)

    def _handle_player_discard(self, player_id: int, uuids: list[str]) -> None:
        """Handle player discard pile update."""
        callback = self.callbacks.get("player_discard")
        if callback:
            callback(player_id, uuids)

    def _handle_player_in_play(self, player_id: int, uuids: list[str]) -> None:
        """Handle player in-play cards update."""
        callback = self.callbacks.get("player_in_play")
        if callback:
            callback(player_id, uuids)
