"""
Example usage of MQTT client module
Run this to test MQTT connectivity and pub/sub

NOTE: This requires a running MQTT broker.
To start a local broker with Docker:
  docker run -it -p 1883:1883 eclipse-mosquitto:2
"""

import logging
import time
from typing import Any

from .config import Config
from .mqtt_client import MQTTClient, Topics

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def test_basic_pubsub():
    """Test basic publish/subscribe functionality"""
    logger.info("=" * 60)
    logger.info("TESTING BASIC PUBLISH/SUBSCRIBE")
    logger.info("=" * 60)

    # Load config
    try:
        config = Config("config.toml")
    except FileNotFoundError:
        logger.error("Configuration file not found. Copy config.toml.example to config.toml")
        return

    # Create client
    client = MQTTClient(
        client_id="test_client",
        broker_host=config.mqtt.broker_host,
        broker_port=config.mqtt.broker_port,
        username=config.mqtt.username if config.mqtt.username else None,
        password=config.mqtt.password if config.mqtt.password else None,
        keepalive=config.mqtt.keepalive,
        reconnect_delay_min=config.mqtt.reconnect_delay_min,
        reconnect_delay_max=config.mqtt.reconnect_delay_max,
    )

    # Set up connection callback
    def on_connect(success: bool):
        if success:
            logger.info("✓ Connected successfully")
        else:
            logger.error("✗ Connection failed")

    client.set_on_connect_callback(on_connect)

    # Set up message callback
    messages_received = []

    def on_message(topic: str, payload: Any):
        logger.info(f"Received on {topic}: {payload}")
        messages_received.append((topic, payload))

    client.set_on_message_callback(on_message)

    # Connect
    logger.info("Connecting to broker...")
    client.connect()

    # Wait for connection
    time.sleep(2)

    if not client.connected:
        logger.error("Failed to connect to broker. Is it running?")
        logger.info("To start a local broker: docker run -it -p 1883:1883 eclipse-mosquitto:2")
        return

    # Subscribe to test topic
    logger.info("Subscribing to test topic...")
    client.subscribe("supershow/test", qos=1)

    # Publish some test messages
    logger.info("Publishing test messages...")
    client.publish("supershow/test", "Hello MQTT!", qos=1)
    client.publish("supershow/test", {"type": "test", "value": 123}, qos=1)

    # Wait for messages
    time.sleep(1)

    # Check results
    logger.info(f"Received {len(messages_received)} messages")

    # Disconnect
    client.disconnect()
    logger.info("Disconnected")


def test_match_state_publishing():
    """Test publishing match state updates"""
    logger.info("=" * 60)
    logger.info("TESTING MATCH STATE PUBLISHING")
    logger.info("=" * 60)

    # Load config
    try:
        config = Config("config.toml")
    except FileNotFoundError:
        logger.error("Configuration file not found")
        return

    # Create controller client
    controller = MQTTClient(
        client_id=config.mqtt.client_id_controller,
        broker_host=config.mqtt.broker_host,
        broker_port=config.mqtt.broker_port,
        username=config.mqtt.username if config.mqtt.username else None,
        password=config.mqtt.password if config.mqtt.password else None,
    )

    # Create production client
    production = MQTTClient(
        client_id=config.mqtt.client_id_production,
        broker_host=config.mqtt.broker_host,
        broker_port=config.mqtt.broker_port,
        username=config.mqtt.username if config.mqtt.username else None,
        password=config.mqtt.password if config.mqtt.password else None,
    )

    # Set up production client to receive updates
    updates_received = []

    def on_state_update(topic: str, payload: Any):
        logger.info(f"Production received: {topic}")
        updates_received.append((topic, payload))

    production.set_on_message_callback(on_state_update)

    # Connect both clients
    logger.info("Connecting clients...")
    controller.connect()
    production.connect()

    time.sleep(2)

    if not controller.connected or not production.connected:
        logger.error("Failed to connect clients")
        controller.disconnect()
        production.disconnect()
        return

    # Subscribe production to all match state topics
    logger.info("Production subscribing to match topics...")
    production.subscribe("supershow/match/#", qos=1)
    production.subscribe("supershow/player/#", qos=1)
    production.subscribe("supershow/events/#", qos=1)

    time.sleep(1)

    # Controller publishes match initialization
    logger.info("Controller publishing match init...")
    match_init = {
        "match_id": "test-match-001",
        "title": "Championship Match",
        "stipulations": "New York Rules",
        "player1_competitor": "comp-uuid-1",
        "player2_competitor": "comp-uuid-2",
    }
    controller.publish(Topics.MATCH_INIT, match_init, qos=1, retain=True)

    # Controller publishes player state updates
    logger.info("Controller publishing player state...")
    controller.publish(
        Topics.player_topic(Topics.PLAYER_COMPETITOR, 1), "competitor-uuid-123", qos=1, retain=True
    )
    controller.publish(Topics.player_topic(Topics.PLAYER_HAND_COUNT, 1), 5, qos=1, retain=True)
    controller.publish(Topics.player_topic(Topics.PLAYER_DECK_COUNT, 1), 25, qos=1, retain=True)

    # Controller publishes turn roll event
    logger.info("Controller publishing turn roll event...")
    turn_roll = {"player_id": 1, "roll_type": "Power", "value": 8, "timestamp": int(time.time())}
    controller.publish(Topics.EVENT_TURN_ROLL, turn_roll, qos=1)

    # Wait for messages to be received
    time.sleep(2)

    # Check results
    logger.info(f"Production received {len(updates_received)} updates:")
    for topic, payload in updates_received:
        logger.info(f"  - {topic}: {str(payload)[:50]}")

    # Disconnect
    controller.disconnect()
    production.disconnect()
    logger.info("Disconnected both clients")


def test_topic_helpers():
    """Test topic formatting helpers"""
    logger.info("=" * 60)
    logger.info("TESTING TOPIC HELPERS")
    logger.info("=" * 60)

    # Test player topic formatting
    player1_competitor = Topics.player_topic(Topics.PLAYER_COMPETITOR, 1)
    player2_competitor = Topics.player_topic(Topics.PLAYER_COMPETITOR, 2)
    player1_hand = Topics.player_topic(Topics.PLAYER_HAND_COUNT, 1)

    logger.info("Player topic examples:")
    logger.info(f"  Player 1 competitor: {player1_competitor}")
    logger.info(f"  Player 2 competitor: {player2_competitor}")
    logger.info(f"  Player 1 hand count: {player1_hand}")

    # List all match topics
    logger.info("\nMatch state topics:")
    logger.info(f"  {Topics.MATCH_INIT}")
    logger.info(f"  {Topics.MATCH_RESET}")
    logger.info(f"  {Topics.MATCH_TITLE}")
    logger.info(f"  {Topics.MATCH_STIPULATIONS}")
    logger.info(f"  {Topics.MATCH_CROWD_METER}")

    # List all event topics
    logger.info("\nEvent topics:")
    logger.info(f"  {Topics.EVENT_MATCH_START}")
    logger.info(f"  {Topics.EVENT_TURN_ROLL}")
    logger.info(f"  {Topics.EVENT_CARD_PLAYED}")
    logger.info(f"  {Topics.EVENT_MATCH_END}")

    # List control topics
    logger.info("\nControl topics:")
    logger.info(f"  {Topics.CONTROL_HEARTBEAT}")
    logger.info(f"  {Topics.CONTROL_READY}")


def test_context_manager():
    """Test context manager usage"""
    logger.info("=" * 60)
    logger.info("TESTING CONTEXT MANAGER")
    logger.info("=" * 60)

    try:
        config = Config("config.toml")
    except FileNotFoundError:
        logger.error("Configuration file not found")
        return

    # Use client as context manager
    with MQTTClient(
        client_id="context_test",
        broker_host=config.mqtt.broker_host,
        broker_port=config.mqtt.broker_port,
    ) as client:
        time.sleep(2)

        if client.connected:
            logger.info("✓ Connected via context manager")
            client.publish("supershow/test", "Context manager test", qos=1)
            logger.info("✓ Published message")
        else:
            logger.error("✗ Failed to connect")

    logger.info("✓ Context manager cleanup complete")


def main():
    """Run all MQTT tests"""
    logger.info("MQTT Client Test Suite")
    logger.info("=" * 60)

    # Test topic helpers (no broker needed)
    test_topic_helpers()

    print()

    # Test basic pub/sub (requires broker)
    logger.info("\nThe following tests require a running MQTT broker.")
    logger.info("To start a local broker:")
    logger.info("  docker run -it -p 1883:1883 eclipse-mosquitto:2")
    logger.info("")

    response = input("Do you have a broker running? (y/n): ")
    if response.lower() != "y":
        logger.info("Skipping broker tests")
        return

    print()
    test_basic_pubsub()

    print()
    test_match_state_publishing()

    print()
    test_context_manager()

    logger.info("=" * 60)
    logger.info("All tests complete!")


if __name__ == "__main__":
    main()
