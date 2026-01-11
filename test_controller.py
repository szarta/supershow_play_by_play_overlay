"""
Test script to monitor MQTT messages from the controller.

Run this script in a separate terminal while using the controller app
to verify that all state changes are being published correctly.
"""

import logging

from src.shared.mqtt_client import MQTTClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)

received_messages = []


def on_message(topic: str, payload):
    """Callback for received messages."""
    logger.info(f"📨 {topic}: {payload}")
    received_messages.append((topic, payload))


def main():
    """Subscribe to all supershow topics and monitor messages."""
    logger.info("Starting MQTT monitor...")
    logger.info("=" * 60)

    # Create subscriber client
    mqtt = MQTTClient(client_id="test_subscriber", broker_host="localhost", broker_port=1883)

    # Connect
    mqtt.connect()

    # Subscribe to all supershow topics
    mqtt.subscribe("supershow/#", on_message)

    logger.info("Subscribed to supershow/#")
    logger.info("Waiting for messages from controller...")
    logger.info("=" * 60)
    logger.info("")

    try:
        # Keep running
        import time

        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("\n\nReceived Ctrl+C, shutting down...")
        mqtt.disconnect()
        logger.info(f"Total messages received: {len(received_messages)}")


if __name__ == "__main__":
    main()
