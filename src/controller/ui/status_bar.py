"""
Status bar component for displaying MQTT connection status.
"""

import tkinter as tk
from tkinter import ttk


class StatusBar(ttk.Frame):
    """Status bar showing MQTT connection status."""

    def __init__(self, parent):
        """
        Initialize the status bar.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        # Create label for MQTT status
        self.mqtt_label = ttk.Label(self, text="MQTT:")
        self.mqtt_label.pack(side=tk.LEFT, padx=5)

        # Create status indicator
        self.status_label = ttk.Label(self, text="Disconnected", foreground="red")
        self.status_label.pack(side=tk.LEFT, padx=5)

    def update_mqtt_status(self, connected: bool) -> None:
        """
        Update MQTT connection status display.

        This method is thread-safe and can be called from MQTT callbacks.

        Args:
            connected: True if connected, False otherwise
        """
        # Schedule update on main thread
        self.after(0, self._update_status_impl, connected)

    def _update_status_impl(self, connected: bool) -> None:
        """Internal implementation of status update (runs on main thread)."""
        if connected:
            self.status_label.config(text="Connected", foreground="green")
        else:
            self.status_label.config(text="Disconnected", foreground="red")
