"""
MQTT client module for BPP Supershow Overlay
Handles MQTT connection, publishing, and subscribing
"""
import json
import logging
import time
from typing import Optional, Callable, Dict, Any
from dataclasses import dataclass

import paho.mqtt.client as mqtt

logger = logging.getLogger(__name__)


# ==================== Topic Constants ====================

class Topics:
    """MQTT topic constants"""

    # State topics (published by Controller)
    MATCH_INIT = "supershow/match/init"
    MATCH_RESET = "supershow/match/reset"
    MATCH_TITLE = "supershow/match/title"
    MATCH_STIPULATIONS = "supershow/match/stipulations"
    MATCH_CROWD_METER = "supershow/match/crowd_meter"

    # Player state topics
    PLAYER_COMPETITOR = "supershow/player/{player_id}/competitor"
    PLAYER_HAND_COUNT = "supershow/player/{player_id}/hand_count"
    PLAYER_DECK_COUNT = "supershow/player/{player_id}/deck_count"
    PLAYER_DISCARD = "supershow/player/{player_id}/discard"
    PLAYER_IN_PLAY = "supershow/player/{player_id}/in_play"
    PLAYER_TURN_ROLL = "supershow/player/{player_id}/turn_roll"
    PLAYER_TURNS_WON = "supershow/player/{player_id}/turns_won"
    PLAYER_TURNS_PASSED = "supershow/player/{player_id}/turns_passed"

    # Event topics (for match recording)
    EVENT_MATCH_START = "supershow/events/match_start"
    EVENT_TURN_ROLL = "supershow/events/turn_roll"
    EVENT_CARD_PLAYED = "supershow/events/card_played"
    EVENT_CARD_STOPPED = "supershow/events/card_stopped"
    EVENT_CARD_DISCARDED = "supershow/events/card_discarded"
    EVENT_CARD_TO_HAND = "supershow/events/card_to_hand"
    EVENT_CARD_BURIED = "supershow/events/card_buried"
    EVENT_CARD_TOPPED = "supershow/events/card_topped"
    EVENT_TURN_WON = "supershow/events/turn_won"
    EVENT_TURN_PASSED = "supershow/events/turn_passed"
    EVENT_CROWD_INCREMENT = "supershow/events/crowd_increment"
    EVENT_MATCH_END = "supershow/events/match_end"

    # Control topics (Production → Controller)
    CONTROL_HEARTBEAT = "supershow/control/heartbeat"
    CONTROL_READY = "supershow/control/ready"

    @classmethod
    def player_topic(cls, base_topic: str, player_id: int) -> str:
        """
        Format a player-specific topic

        Args:
            base_topic: Topic template with {player_id} placeholder
            player_id: Player ID (1 or 2)

        Returns:
            Formatted topic string
        """
        return base_topic.format(player_id=player_id)


# ==================== MQTT Client ====================

class MQTTClient:
    """MQTT client wrapper with reconnection logic"""

    def __init__(
        self,
        client_id: str,
        broker_host: str,
        broker_port: int,
        username: Optional[str] = None,
        password: Optional[str] = None,
        keepalive: int = 60,
        reconnect_delay_min: int = 1,
        reconnect_delay_max: int = 60
    ):
        """
        Initialize MQTT client

        Args:
            client_id: Unique client identifier
            broker_host: MQTT broker hostname
            broker_port: MQTT broker port
            username: Optional username for authentication
            password: Optional password for authentication
            keepalive: Keepalive interval in seconds
            reconnect_delay_min: Minimum reconnect delay in seconds
            reconnect_delay_max: Maximum reconnect delay in seconds
        """
        self.client_id = client_id
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.username = username
        self.password = password
        self.keepalive = keepalive
        self.reconnect_delay_min = reconnect_delay_min
        self.reconnect_delay_max = reconnect_delay_max

        # Create client instance
        self.client = mqtt.Client(client_id=client_id)

        # Set authentication if provided
        if username and password:
            self.client.username_pw_set(username, password)

        # Connection state
        self.connected = False
        self.reconnect_delay = reconnect_delay_min

        # Callback handlers
        self.on_connect_callback: Optional[Callable[[bool], None]] = None
        self.on_disconnect_callback: Optional[Callable[[], None]] = None
        self.on_message_callback: Optional[Callable[[str, Any], None]] = None

        # Message handlers by topic
        self.topic_handlers: Dict[str, Callable[[Any], None]] = {}

        # Set up internal callbacks
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message

        logger.info(f"MQTT client initialized: {client_id}")

    def connect(self) -> bool:
        """
        Connect to MQTT broker

        Returns:
            True if connection initiated successfully
        """
        try:
            logger.info(
                f"Connecting to MQTT broker: {self.broker_host}:{self.broker_port}"
            )
            self.client.connect(
                self.broker_host,
                self.broker_port,
                self.keepalive
            )
            self.client.loop_start()
            return True
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")
            return False

    def disconnect(self) -> None:
        """Disconnect from MQTT broker"""
        logger.info("Disconnecting from MQTT broker")
        self.client.loop_stop()
        self.client.disconnect()
        self.connected = False

    def publish(
        self,
        topic: str,
        payload: Any,
        qos: int = 0,
        retain: bool = False
    ) -> bool:
        """
        Publish message to topic

        Args:
            topic: MQTT topic
            payload: Message payload (will be JSON-encoded if not string)
            qos: Quality of Service (0, 1, or 2)
            retain: Whether to retain message

        Returns:
            True if publish was successful
        """
        if not self.connected:
            logger.warning(f"Cannot publish to {topic}: not connected")
            return False

        try:
            # Convert payload to JSON if not string
            if isinstance(payload, str):
                message = payload
            else:
                message = json.dumps(payload)

            result = self.client.publish(topic, message, qos=qos, retain=retain)

            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.debug(f"Published to {topic}: {message[:100]}")
                return True
            else:
                logger.error(f"Failed to publish to {topic}: {result.rc}")
                return False

        except Exception as e:
            logger.error(f"Error publishing to {topic}: {e}")
            return False

    def subscribe(
        self,
        topic: str,
        qos: int = 0,
        handler: Optional[Callable[[Any], None]] = None
    ) -> bool:
        """
        Subscribe to topic

        Args:
            topic: MQTT topic (supports wildcards)
            qos: Quality of Service (0, 1, or 2)
            handler: Optional handler function for this topic

        Returns:
            True if subscription was successful
        """
        if not self.connected:
            logger.warning(f"Cannot subscribe to {topic}: not connected")
            return False

        try:
            result = self.client.subscribe(topic, qos=qos)

            if result[0] == mqtt.MQTT_ERR_SUCCESS:
                logger.info(f"Subscribed to {topic}")
                if handler:
                    self.topic_handlers[topic] = handler
                return True
            else:
                logger.error(f"Failed to subscribe to {topic}: {result[0]}")
                return False

        except Exception as e:
            logger.error(f"Error subscribing to {topic}: {e}")
            return False

    def unsubscribe(self, topic: str) -> bool:
        """
        Unsubscribe from topic

        Args:
            topic: MQTT topic

        Returns:
            True if unsubscription was successful
        """
        try:
            result = self.client.unsubscribe(topic)

            if result[0] == mqtt.MQTT_ERR_SUCCESS:
                logger.info(f"Unsubscribed from {topic}")
                if topic in self.topic_handlers:
                    del self.topic_handlers[topic]
                return True
            else:
                logger.error(f"Failed to unsubscribe from {topic}: {result[0]}")
                return False

        except Exception as e:
            logger.error(f"Error unsubscribing from {topic}: {e}")
            return False

    def set_on_connect_callback(self, callback: Callable[[bool], None]) -> None:
        """
        Set callback for connection events

        Args:
            callback: Function to call with connection status
        """
        self.on_connect_callback = callback

    def set_on_disconnect_callback(self, callback: Callable[[], None]) -> None:
        """
        Set callback for disconnection events

        Args:
            callback: Function to call on disconnect
        """
        self.on_disconnect_callback = callback

    def set_on_message_callback(
        self,
        callback: Callable[[str, Any], None]
    ) -> None:
        """
        Set global message callback

        Args:
            callback: Function to call with (topic, payload)
        """
        self.on_message_callback = callback

    # ==================== Internal Callbacks ====================

    def _on_connect(
        self,
        client: mqtt.Client,
        userdata: Any,
        flags: Dict[str, Any],
        rc: int
    ) -> None:
        """
        Internal connection callback

        Args:
            client: MQTT client instance
            userdata: User data
            flags: Response flags
            rc: Connection result code
        """
        if rc == 0:
            logger.info("Connected to MQTT broker")
            self.connected = True
            self.reconnect_delay = self.reconnect_delay_min

            if self.on_connect_callback:
                self.on_connect_callback(True)
        else:
            logger.error(f"Connection failed with code {rc}")
            self.connected = False

            if self.on_connect_callback:
                self.on_connect_callback(False)

    def _on_disconnect(
        self,
        client: mqtt.Client,
        userdata: Any,
        rc: int
    ) -> None:
        """
        Internal disconnection callback

        Args:
            client: MQTT client instance
            userdata: User data
            rc: Disconnection result code
        """
        self.connected = False

        if rc == 0:
            logger.info("Disconnected from MQTT broker (clean)")
        else:
            logger.warning(f"Disconnected from MQTT broker (code {rc})")

            # Exponential backoff for reconnection
            logger.info(f"Reconnecting in {self.reconnect_delay} seconds...")
            time.sleep(self.reconnect_delay)

            self.reconnect_delay = min(
                self.reconnect_delay * 2,
                self.reconnect_delay_max
            )

            try:
                self.client.reconnect()
            except Exception as e:
                logger.error(f"Reconnection failed: {e}")

        if self.on_disconnect_callback:
            self.on_disconnect_callback()

    def _on_message(
        self,
        client: mqtt.Client,
        userdata: Any,
        message: mqtt.MQTTMessage
    ) -> None:
        """
        Internal message callback

        Args:
            client: MQTT client instance
            userdata: User data
            message: MQTT message
        """
        topic = message.topic
        payload_str = message.payload.decode('utf-8')

        # Try to parse as JSON
        try:
            payload = json.loads(payload_str)
        except json.JSONDecodeError:
            payload = payload_str

        logger.debug(f"Received message on {topic}: {str(payload)[:100]}")

        # Call topic-specific handler if registered
        if topic in self.topic_handlers:
            try:
                self.topic_handlers[topic](payload)
            except Exception as e:
                logger.error(f"Error in topic handler for {topic}: {e}")

        # Call global message callback
        if self.on_message_callback:
            try:
                self.on_message_callback(topic, payload)
            except Exception as e:
                logger.error(f"Error in message callback for {topic}: {e}")

    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()


# ==================== Helper Functions ====================

def create_controller_client(
    broker_host: str,
    broker_port: int,
    client_id: str = "supershow_controller",
    username: Optional[str] = None,
    password: Optional[str] = None,
    **kwargs
) -> MQTTClient:
    """
    Create MQTT client for controller app

    Args:
        broker_host: MQTT broker hostname
        broker_port: MQTT broker port
        client_id: Client identifier
        username: Optional username
        password: Optional password
        **kwargs: Additional MQTTClient arguments

    Returns:
        MQTTClient instance
    """
    return MQTTClient(
        client_id=client_id,
        broker_host=broker_host,
        broker_port=broker_port,
        username=username,
        password=password,
        **kwargs
    )


def create_production_client(
    broker_host: str,
    broker_port: int,
    client_id: str = "supershow_production",
    username: Optional[str] = None,
    password: Optional[str] = None,
    **kwargs
) -> MQTTClient:
    """
    Create MQTT client for production view app

    Args:
        broker_host: MQTT broker hostname
        broker_port: MQTT broker port
        client_id: Client identifier
        username: Optional username
        password: Optional password
        **kwargs: Additional MQTTClient arguments

    Returns:
        MQTTClient instance
    """
    return MQTTClient(
        client_id=client_id,
        broker_host=broker_host,
        broker_port=broker_port,
        username=username,
        password=password,
        **kwargs
    )
