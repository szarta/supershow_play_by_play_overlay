"""
Controller application entry point.

This module initializes the controller application, sets up all services
(config, database, MQTT), and launches the UI.
"""

import logging
import sys
import time
import tkinter as tk
from tkinter import messagebox

from ..shared.config import Config
from ..shared.database import DatabaseService
from ..shared.mqtt_client import MQTTClient
from .controller import MatchController
from .ui.main_window import MainWindow


def setup_logging():
    """Setup logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def main():
    """Main entry point for the controller application."""
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting controller application...")

    # Load configuration
    try:
        config = Config("config.toml")
        logger.info("Configuration loaded")
    except FileNotFoundError as e:
        # Show error dialog (without parent window yet)
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Configuration Error",
            f"Failed to load configuration file: {e}\n\n"
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
            f"Failed to connect to database at {config.database.cards_db_path}\n\n"
            f"Error: {e}\n\n"
            "Please run the sync script to initialize the database.",
        )
        root.destroy()
        return 1

    # Create MQTT client
    mqtt_client = MQTTClient(
        client_id=config.mqtt.client_id_controller,
        broker_host=config.mqtt.broker_host,
        broker_port=config.mqtt.broker_port,
        username=config.mqtt.username if config.mqtt.username else None,
        password=config.mqtt.password if config.mqtt.password else None,
        keepalive=config.mqtt.keepalive,
    )

    # Create controller
    controller = MatchController(config, db_service, mqtt_client)

    # Load competitors
    try:
        competitor_names = controller.load_competitors()
        logger.info(f"Loaded {len(competitor_names)} competitors")

        if len(competitor_names) == 0:
            root = tk.Tk()
            root.withdraw()
            messagebox.showwarning(
                "No Competitors Found",
                "The database contains no competitor cards.\n\n"
                "Please run the sync script to download card data.\n\n"
                "The application will continue, but you won't be able to select competitors.",
            )
            root.destroy()

    except Exception as e:
        logger.error(f"Failed to load competitors: {e}")
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Database Error", f"Failed to load competitors from database: {e}")
        root.destroy()
        return 1

    # Create UI
    root = tk.Tk()

    # Store reference to UI for MQTT callback
    ui = None

    # Setup MQTT callbacks
    def on_mqtt_connect(success: bool):
        """Called when MQTT connection status changes."""
        status = "Connected" if success else "Failed"
        logger.info(f"MQTT: {status}")
        if ui:
            ui.update_mqtt_status(success)

    mqtt_client.set_on_connect_callback(on_mqtt_connect)

    # Connect to MQTT broker
    logger.info(f"Connecting to MQTT broker at {config.mqtt.broker_host}:{config.mqtt.broker_port}")
    mqtt_client.connect()

    # Wait briefly for connection
    time.sleep(2)

    # Check connection status
    if not mqtt_client.connected:
        response = messagebox.askretrycancel(
            "MQTT Connection Failed",
            f"Failed to connect to MQTT broker at {config.mqtt.broker_host}:{config.mqtt.broker_port}\n\n"
            "The controller will work in offline mode, but state will not be published.\n\n"
            "Retry connection?",
        )
        if response:
            mqtt_client.connect()
            time.sleep(2)
        else:
            logger.warning("Continuing in offline mode")

    # Create main window
    ui = MainWindow(root, config, controller, competitor_names)

    # Update initial MQTT status
    ui.update_mqtt_status(mqtt_client.connected)

    # Handle window close
    def on_closing():
        """Called when window is closing."""
        logger.info("Shutting down...")
        mqtt_client.disconnect()
        db_service.disconnect()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    # Start UI main loop
    logger.info("Controller application started")
    root.mainloop()

    logger.info("Controller application exited")
    return 0


if __name__ == "__main__":
    sys.exit(main())
