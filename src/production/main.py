"""
Production view application entry point.

Initializes the production overlay window and connects to MQTT for state updates.
"""

import logging
import sys
import tkinter as tk
from tkinter import messagebox

from ..shared.config import Config
from ..shared.database import DatabaseService
from ..shared.mqtt_client import MQTTClient
from .state_manager import ProductionStateManager
from .subscriber import ProductionSubscriber
from .ui.overlay_window import OverlayWindow


def setup_logging() -> None:
    """Setup logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def main() -> int:
    """Main entry point for the production view application."""
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting production view application...")

    # Load configuration
    try:
        config = Config("config.toml")
        logger.info("Configuration loaded")
    except FileNotFoundError as e:
        # Show error dialog
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Configuration Error",
            f"Failed to load configuration file: {e}\\n\\n"
            "Please ensure config.toml exists in the project root.",
        )
        root.destroy()
        return 1
    except Exception as e:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Configuration Error", f"Error loading configuration: {e}")
        root.destroy()
        return 1

    # Connect to database
    try:
        db_service = DatabaseService(config.database.cards_db_path)
        db_service.connect()
        card_count = db_service.get_card_count()
        logger.info(f"Database connected: {card_count} cards")
    except Exception as e:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Database Error",
            f"Failed to connect to database at {config.database.cards_db_path}\\n\\n"
            f"Error: {e}\\n\\n"
            "Please run the sync script to initialize the database.",
        )
        root.destroy()
        return 1

    # Create MQTT client
    mqtt_client = MQTTClient(
        client_id=config.mqtt.client_id_production,
        broker_host=config.mqtt.broker_host,
        broker_port=config.mqtt.broker_port,
        username=config.mqtt.username if config.mqtt.username else None,
        password=config.mqtt.password if config.mqtt.password else None,
        keepalive=config.mqtt.keepalive,
    )

    # Create state manager
    state_manager = ProductionStateManager(db_service)

    # Create subscriber
    subscriber = ProductionSubscriber(mqtt_client)

    # Wire subscriber callbacks to state manager
    subscriber.set_callback("match_init", state_manager.update_match_init)
    subscriber.set_callback("match_reset", state_manager.update_match_reset)
    subscriber.set_callback("match_title", state_manager.update_match_title)
    subscriber.set_callback("match_stipulations", state_manager.update_match_stipulations)
    subscriber.set_callback("crowd_meter", state_manager.update_crowd_meter)
    subscriber.set_callback("player_competitor", state_manager.update_player_competitor)
    subscriber.set_callback("player_hand_count", state_manager.update_player_hand_count)
    subscriber.set_callback("player_deck_count", state_manager.update_player_deck_count)
    subscriber.set_callback("player_turn_roll", state_manager.update_player_turn_roll)
    subscriber.set_callback("player_turns_passed", state_manager.update_player_turns_passed)
    subscriber.set_callback("player_finish_roll", state_manager.update_player_finish_roll)
    subscriber.set_callback("player_breakout_rolls", state_manager.update_player_breakout_rolls)
    subscriber.set_callback("player_discard", state_manager.update_player_discard)
    subscriber.set_callback("player_in_play", state_manager.update_player_in_play)

    # Create UI
    root = tk.Tk()
    overlay_window = OverlayWindow(root, config)

    # Wire state manager UI callback to overlay window
    state_manager.set_ui_callback(overlay_window.on_state_update)

    # Connect to MQTT broker
    logger.info(f"Connecting to MQTT broker at {config.mqtt.broker_host}:{config.mqtt.broker_port}")

    try:
        mqtt_client.connect()
        # Subscribe to all supershow topics
        subscriber.subscribe_all()
        logger.info("MQTT connected and subscribed")
    except Exception as e:
        logger.warning(f"MQTT connection failed: {e}")
        messagebox.showwarning(
            "MQTT Connection Failed",
            f"Failed to connect to MQTT broker at {config.mqtt.broker_host}:{config.mqtt.broker_port}\\n\\n"
            "The production view will continue running, but will not receive match updates.\\n\\n"
            "Please check that the MQTT broker is running.",
        )

    # Handle window close
    def on_closing() -> None:
        """Called when window is closing."""
        logger.info("Shutting down...")
        mqtt_client.disconnect()
        db_service.disconnect()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    # Start UI main loop
    logger.info("Production view application started")
    root.mainloop()

    logger.info("Production view application exited")
    return 0


if __name__ == "__main__":
    sys.exit(main())
