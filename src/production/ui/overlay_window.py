"""
Overlay window for production view.

Manages frameless window, expand/collapse, dragging, and auto-collapse timer.
"""

import logging
import tkinter as tk

from ...shared.config import Config
from .collapsed_view import CollapsedView
from .expanded_view import ExpandedView

logger = logging.getLogger(__name__)


class OverlayWindow:
    """Main overlay window with collapsed and expanded views."""

    def __init__(self, root: tk.Tk, config: Config):
        """
        Initialize overlay window.

        Args:
            root: Tkinter root window
            config: Configuration
        """
        self.root = root
        self.config = config
        self.is_expanded = False
        self.auto_collapse_timer: str | None = None

        # For dragging
        self.drag_x = 0
        self.drag_y = 0

        # Configure window
        self._configure_window()

        # Create views
        self._create_views()

        # Setup dragging
        self._setup_dragging()

        # Show collapsed view by default
        self.collapse()

    def _configure_window(self) -> None:
        """Configure the overlay window (frameless, transparent, always on top)."""
        # Window title
        self.root.title("BPP Supershow - Production View")

        # Frameless
        self.root.overrideredirect(True)

        # Always on top
        self.root.wm_attributes("-topmost", True)

        # Semi-transparent
        self.root.wm_attributes("-alpha", self.config.production_ui.window_opacity)

        # Background color
        bg_color = self.config.production_ui.background_color
        self.root.configure(bg=bg_color)

        # Initial size (collapsed)
        window_width = self.config.production_ui.default_width
        window_height = self.config.production_ui.default_height

        # Position at bottom of screen
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2  # Center horizontally
        y = screen_height - window_height  # Bottom of screen

        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

        logger.info(f"Window configured: {window_width}x{window_height} at ({x}, {y})")

    def _create_views(self) -> None:
        """Create collapsed and expanded views."""
        # Container frame
        self.container = tk.Frame(self.root, bg=self.config.production_ui.background_color)
        self.container.pack(fill=tk.BOTH, expand=True)

        # Create views
        self.collapsed_view = CollapsedView(
            self.container, self.config, on_player_click=self.expand
        )

        self.expanded_view = ExpandedView(self.container, self.config, on_collapse=self.collapse)

    def _setup_dragging(self) -> None:
        """Setup window dragging."""
        self.root.bind("<Button-1>", self._start_drag)
        self.root.bind("<B1-Motion>", self._do_drag)

    def _start_drag(self, event: tk.Event) -> None:
        """Save initial mouse position for dragging."""
        self.drag_x = event.x
        self.drag_y = event.y
        self.reset_auto_collapse_timer()

    def _do_drag(self, event: tk.Event) -> None:
        """Move window based on mouse drag."""
        # Calculate delta
        deltax = event.x - self.drag_x
        deltay = event.y - self.drag_y

        # Get current position
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay

        # Move window
        self.root.geometry(f"+{x}+{y}")

    # ==================== Expand/Collapse ====================

    def expand(self, player_id: int) -> None:
        """
        Expand to detailed view.

        Args:
            player_id: Player ID that was clicked (1 or 2)
        """
        logger.info(f"Expanding view for player {player_id}")

        if self.is_expanded:
            return

        # Hide collapsed view
        self.collapsed_view.pack_forget()

        # Show expanded view
        self.expanded_view.pack(fill=tk.BOTH, expand=True)

        # Resize window
        window_width = self.config.production_ui.default_width
        window_height = self.config.production_ui.expanded_height

        # Keep window at bottom of screen
        screen_height = self.root.winfo_screenheight()
        x = self.root.winfo_x()
        y = screen_height - window_height

        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

        self.is_expanded = True

        # Reset auto-collapse timer
        self.reset_auto_collapse_timer()

    def collapse(self) -> None:
        """Collapse to minimal view."""
        logger.info("Collapsing view")

        if not self.is_expanded and self.collapsed_view.winfo_ismapped():
            return

        # Hide expanded view
        self.expanded_view.pack_forget()

        # Show collapsed view
        self.collapsed_view.pack(fill=tk.BOTH, expand=True)

        # Resize window
        window_width = self.config.production_ui.default_width
        window_height = self.config.production_ui.default_height

        # Keep window at bottom of screen
        screen_height = self.root.winfo_screenheight()
        x = self.root.winfo_x()
        y = screen_height - window_height

        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

        self.is_expanded = False

        # Cancel auto-collapse timer
        if self.auto_collapse_timer:
            self.root.after_cancel(self.auto_collapse_timer)
            self.auto_collapse_timer = None

    def reset_auto_collapse_timer(self) -> None:
        """Reset the auto-collapse timer."""
        # Cancel existing timer
        if self.auto_collapse_timer:
            self.root.after_cancel(self.auto_collapse_timer)

        # Start new timer if expanded
        if self.is_expanded:
            delay_ms = self.config.production_ui.auto_collapse_seconds * 1000
            self.auto_collapse_timer = self.root.after(delay_ms, self.collapse)

    # ==================== State Update Handlers ====================

    def on_state_update(self, update_type: str, data: dict) -> None:
        """
        Handle state updates from state manager.

        Args:
            update_type: Type of update (e.g., 'match_title', 'player_competitor')
            data: Update data
        """
        try:
            if update_type == "match_init":
                self.collapsed_view.update_match_title(data["title"])
                self.collapsed_view.update_match_stipulations(data["stipulations"])
                self.collapsed_view.update_crowd_meter(data["crowd_meter"])
                self.expanded_view.update_match_title(data["title"])
                self.expanded_view.update_match_stipulations(data["stipulations"])
                self.expanded_view.update_crowd_meter(data["crowd_meter"])

            elif update_type == "match_reset":
                self.collapsed_view.update_match_title("")
                self.collapsed_view.update_match_stipulations("")
                self.collapsed_view.update_crowd_meter(0)
                self.expanded_view.update_match_title("")
                self.expanded_view.update_match_stipulations("")
                self.expanded_view.update_crowd_meter(0)

            elif update_type == "match_title":
                self.collapsed_view.update_match_title(data["title"])
                self.expanded_view.update_match_title(data["title"])

            elif update_type == "match_stipulations":
                self.collapsed_view.update_match_stipulations(data["stipulations"])
                self.expanded_view.update_match_stipulations(data["stipulations"])

            elif update_type == "crowd_meter":
                self.collapsed_view.update_crowd_meter(data["value"])
                self.expanded_view.update_crowd_meter(data["value"])

            elif update_type == "player_competitor":
                player_id = data["player_id"]
                competitor_card = data["competitor_card"]
                self.collapsed_view.update_player_competitor(player_id, competitor_card)
                self.expanded_view.update_player_competitor(player_id, competitor_card)

            elif update_type == "player_hand_count":
                player_id = data["player_id"]
                count = data["count"]
                self.collapsed_view.update_player_hand_count(player_id, count)
                self.expanded_view.update_player_hand_count(player_id, count)

            elif update_type == "player_deck_count":
                player_id = data["player_id"]
                count = data["count"]
                self.collapsed_view.update_player_deck_count(player_id, count)
                self.expanded_view.update_player_deck_count(player_id, count)

            elif update_type == "player_turn_roll":
                player_id = data["player_id"]
                roll_type = data["roll_type"]
                value = data["value"]
                self.collapsed_view.update_player_turn_roll(player_id, roll_type, value)
                self.expanded_view.update_player_turn_roll(player_id, roll_type, value)

            elif update_type == "player_turns_passed":
                player_id = data["player_id"]
                count = data["count"]
                self.collapsed_view.update_player_turns_passed(player_id, count)
                self.expanded_view.update_player_turns_passed(player_id, count)

            elif update_type == "player_finish_roll":
                player_id = data["player_id"]
                value = data["value"]
                self.collapsed_view.update_player_finish_roll(player_id, value)
                self.expanded_view.update_player_finish_roll(player_id, value)

            elif update_type == "player_breakout_rolls":
                player_id = data["player_id"]
                rolls = data["rolls"]
                self.collapsed_view.update_player_breakout_rolls(player_id, rolls)
                self.expanded_view.update_player_breakout_rolls(player_id, rolls)

            # Phase 2: player_discard, player_in_play

        except Exception as e:
            logger.error(f"Error handling state update {update_type}: {e}", exc_info=True)
