"""
Main window for the controller application.

Creates the main application window and lays out all UI components.
"""

import tkinter as tk
from tkinter import messagebox, ttk

from ...shared.config import Config
from ..controller import MatchController
from .match_setup_frame import MatchSetupFrame
from .player_frame import PlayerFrame
from .status_bar import StatusBar


class MainWindow:
    """Main application window."""

    def __init__(
        self, root: tk.Tk, config: Config, controller: MatchController, competitor_names: list[str]
    ):
        """
        Initialize the main window.

        Args:
            root: Tkinter root window
            config: Application configuration
            controller: Match controller instance
            competitor_names: List of competitor names
        """
        self.root = root
        self.config = config
        self.controller = controller
        self.competitor_names = competitor_names

        # Configure window
        self.root.title("Big Pro Presents - Controller")
        self.root.geometry("1000x700")

        # Apply theme
        style = ttk.Style()
        if self.config.controller_ui.theme == "dark":
            # Try to use a dark theme if available
            try:
                style.theme_use("clam")
            except tk.TclError:
                pass

        # Create UI components
        self._create_widgets()

        # Enable live editing callbacks after widgets are created
        self.match_setup_frame.enable_live_editing_callbacks()

    def _create_widgets(self) -> None:
        """Create all widgets for the main window."""
        # Top frame - Match Setup
        top_frame = ttk.Frame(self.root)
        top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        self.match_setup_frame = MatchSetupFrame(
            top_frame,
            competitor_names=self.competitor_names,
            on_start_match=self._handle_start_match,
            on_reset_match=self._handle_reset_match,
            on_quit=self._handle_quit,
            on_title_changed=self.controller.update_title,
            on_stipulations_changed=self.controller.update_stipulations,
            on_crowd_meter_changed=self.controller.update_crowd_meter,
        )
        self.match_setup_frame.pack(fill=tk.X)

        # Middle frame - Player states (side by side)
        middle_frame = ttk.Frame(self.root)
        middle_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Player 1 frame
        self.player1_frame = PlayerFrame(
            middle_frame,
            player_id=1,
            on_update_roll=self._handle_update_roll,
            on_increment_hand=self._handle_increment_hand,
            on_decrement_hand=self._handle_decrement_hand,
            on_update_finish_roll=self._handle_update_finish_roll,
            on_add_breakout_roll=self._handle_add_breakout_roll,
            on_clear_breakout_rolls=self._handle_clear_breakout_rolls,
            on_increment_turns_passed=self._handle_increment_turns_passed,
        )
        self.player1_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        # Player 2 frame
        self.player2_frame = PlayerFrame(
            middle_frame,
            player_id=2,
            on_update_roll=self._handle_update_roll,
            on_increment_hand=self._handle_increment_hand,
            on_decrement_hand=self._handle_decrement_hand,
            on_update_finish_roll=self._handle_update_finish_roll,
            on_add_breakout_roll=self._handle_add_breakout_roll,
            on_clear_breakout_rolls=self._handle_clear_breakout_rolls,
            on_increment_turns_passed=self._handle_increment_turns_passed,
        )
        self.player2_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        # Bottom frame - Status bar
        bottom_frame = ttk.Frame(self.root)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.status_bar = StatusBar(bottom_frame)
        self.status_bar.pack(fill=tk.X, padx=5, pady=5)

    def _handle_start_match(
        self, title: str, stipulations: str, crowd_meter: int, p1_name: str, p2_name: str
    ) -> None:
        """Handle start match request."""
        # Validate MQTT connection
        if not self.controller.is_mqtt_connected():
            response = messagebox.askyesno(
                "MQTT Disconnected",
                "MQTT broker is not connected. Match state will not be published.\n\n"
                "Continue anyway?",
            )
            if not response:
                return

        # Get competitor UUIDs
        p1_competitor = self.controller.get_competitor_by_name(p1_name)
        p2_competitor = self.controller.get_competitor_by_name(p2_name)

        if not p1_competitor:
            messagebox.showerror(
                "Invalid Competitor", f"Player 1 competitor '{p1_name}' not found in database"
            )
            return

        if not p2_competitor:
            messagebox.showerror(
                "Invalid Competitor", f"Player 2 competitor '{p2_name}' not found in database"
            )
            return

        # Start match
        try:
            self.controller.start_match(
                title=title,
                stipulations=stipulations,
                crowd_meter=crowd_meter,
                p1_competitor_uuid=p1_competitor.db_uuid,
                p2_competitor_uuid=p2_competitor.db_uuid,
            )

            # Update player displays
            self._update_player_displays()

            messagebox.showinfo("Match Started", f"Match started: {title}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to start match: {e}")

    def _handle_reset_match(self) -> None:
        """Handle reset match request."""
        response = messagebox.askyesno(
            "Reset Match",
            "Are you sure you want to reset the match?\n\n"
            "This will clear all match state and publish a reset signal.",
        )

        if response:
            self.controller.reset_match()
            self._update_player_displays()
            messagebox.showinfo("Match Reset", "Match has been reset")

    def _handle_quit(self) -> None:
        """Handle quit button."""
        self.root.quit()

    def _handle_update_roll(self, player_id: int, roll_type, value: int) -> None:
        """Handle turn roll update."""
        self.controller.update_turn_roll(player_id, roll_type, value)

    def _handle_increment_hand(self, player_id: int) -> None:
        """Handle hand count increment."""
        self.controller.increment_hand_count(player_id)
        self._update_player_display(player_id)

    def _handle_decrement_hand(self, player_id: int) -> None:
        """Handle hand count decrement."""
        self.controller.decrement_hand_count(player_id)
        self._update_player_display(player_id)

    def _handle_update_finish_roll(self, player_id: int, value: int | None) -> None:
        """Handle finish roll update."""
        self.controller.update_finish_roll(player_id, value)
        self._update_player_display(player_id)

    def _handle_add_breakout_roll(self, player_id: int, value: int) -> None:
        """Handle adding breakout roll."""
        self.controller.add_breakout_roll(player_id, value)
        self._update_player_display(player_id)

    def _handle_clear_breakout_rolls(self, player_id: int) -> None:
        """Handle clearing breakout rolls."""
        self.controller.clear_breakout_rolls(player_id)
        self._update_player_display(player_id)

    def _handle_increment_turns_passed(self, player_id: int) -> None:
        """Handle turns passed increment."""
        self.controller.increment_turns_passed(player_id)
        self._update_player_display(player_id)

    def _update_player_display(self, player_id: int) -> None:
        """Update specific player display."""
        player_state = self.controller.get_player_state(player_id)

        if player_id == 1:
            self.player1_frame.update_display(player_state)
        elif player_id == 2:
            self.player2_frame.update_display(player_state)

    def _update_player_displays(self) -> None:
        """Update both player displays."""
        self._update_player_display(1)
        self._update_player_display(2)

    def update_mqtt_status(self, connected: bool) -> None:
        """Update MQTT connection status display."""
        self.status_bar.update_mqtt_status(connected)
