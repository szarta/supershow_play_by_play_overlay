"""
Expanded view for production overlay.

Displays detailed player information with larger competitor images and full stats.
"""

import logging
import tkinter as tk
from collections.abc import Callable
from pathlib import Path
from tkinter import ttk

from ...shared.config import Config
from ...shared.models import Card, PlayerState, RollType
from .utils import (
    format_roll_display,
    get_roll_color,
    load_competitor_image,
    render_crowd_meter,
)

logger = logging.getLogger(__name__)


class ExpandedView(ttk.Frame):
    """Expanded view (1920x500px by default)."""

    def __init__(
        self,
        parent: tk.Widget,
        config: Config,
        on_collapse: Callable[[], None],
    ):
        """
        Initialize expanded view.

        Args:
            parent: Parent widget
            config: Configuration
            on_collapse: Callback when user wants to collapse
        """
        super().__init__(parent)
        self.config = config
        self.on_collapse = on_collapse
        self.images_path = Path(config.database.images_path)

        # Player state tracking
        self.player_data = {
            1: {"competitor_card": None, "state": PlayerState(player_id=1)},
            2: {"competitor_card": None, "state": PlayerState(player_id=2)},
        }

        # Create widgets
        self._create_widgets()

    def _create_widgets(self) -> None:
        """Create all widgets for expanded view."""
        bg_color = self.config.production_ui.background_color
        text_color = self.config.production_ui.text_color

        self.configure(style="Expanded.TFrame")

        # Bind click on background to collapse
        self.bind("<Button-1>", lambda e: self.on_collapse())

        # Top bar - Match Info
        top_frame = ttk.Frame(self, style="Expanded.TFrame")
        top_frame.pack(fill=tk.X, pady=(5, 0))
        top_frame.bind("<Button-1>", lambda e: self.on_collapse())

        self.title_label = ttk.Label(
            top_frame,
            text="No match started",
            font=("TkDefaultFont", 14, "bold"),
            foreground=text_color,
            background=bg_color,
        )
        self.title_label.pack(side=tk.LEFT, padx=10)
        self.title_label.bind("<Button-1>", lambda e: self.on_collapse())

        self.stipulations_label = ttk.Label(
            top_frame,
            text="",
            font=("TkDefaultFont", 12),
            foreground=text_color,
            background=bg_color,
        )
        self.stipulations_label.pack(side=tk.LEFT, padx=10)
        self.stipulations_label.bind("<Button-1>", lambda e: self.on_collapse())

        self.crowd_label = ttk.Label(
            top_frame,
            text="Crowd: ○○○○○○○○○○",
            font=("TkDefaultFont", 12),
            foreground=text_color,
            background=bg_color,
        )
        self.crowd_label.pack(side=tk.RIGHT, padx=10)
        self.crowd_label.bind("<Button-1>", lambda e: self.on_collapse())

        # Separator
        ttk.Separator(self, orient="horizontal").pack(fill=tk.X, pady=5)

        # Player sections (side by side)
        players_frame = ttk.Frame(self, style="Expanded.TFrame")
        players_frame.pack(fill=tk.BOTH, expand=True)
        players_frame.bind("<Button-1>", lambda e: self.on_collapse())

        # Player 1 (left side)
        self.player1_frame = self._create_player_section(players_frame, 1)
        self.player1_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)

        # Separator
        ttk.Separator(players_frame, orient="vertical").pack(side=tk.LEFT, fill=tk.Y, padx=5)

        # Player 2 (right side)
        self.player2_frame = self._create_player_section(players_frame, 2)
        self.player2_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)

    def _create_player_section(self, parent: tk.Widget, player_id: int) -> ttk.Frame:
        """
        Create detailed player section.

        Args:
            parent: Parent widget
            player_id: Player ID (1 or 2)

        Returns:
            Player section frame
        """
        bg_color = self.config.production_ui.background_color
        text_color = self.config.production_ui.text_color

        # Main frame
        frame = ttk.Frame(parent, style="Expanded.TFrame")

        # Header
        header = ttk.Label(
            frame,
            text=f"PLAYER {player_id}",
            font=("TkDefaultFont", 14, "bold"),
            foreground=text_color,
            background=bg_color,
        )
        header.pack(pady=5)

        # Competitor image (larger)
        img_label = ttk.Label(frame, background=bg_color)
        img_label.pack(pady=10)
        setattr(self, f"player{player_id}_img_label", img_label)

        # Stats frame
        stats_frame = ttk.Frame(frame, style="Expanded.TFrame")
        stats_frame.pack(fill=tk.X, pady=10)

        # Last Roll
        roll_frame = ttk.Frame(stats_frame, style="Expanded.TFrame")
        roll_frame.pack(fill=tk.X, pady=2)

        ttk.Label(
            roll_frame,
            text="Last Roll: ",
            font=("TkDefaultFont", 11),
            foreground=text_color,
            background=bg_color,
        ).pack(side=tk.LEFT)

        roll_value_label = ttk.Label(
            roll_frame,
            text="",
            font=("TkDefaultFont", 11),
            foreground=text_color,
            background=bg_color,
        )
        roll_value_label.pack(side=tk.LEFT)
        setattr(self, f"player{player_id}_roll_label", roll_value_label)

        # Finish Roll
        finish_label = ttk.Label(
            stats_frame,
            text="",
            font=("TkDefaultFont", 11),
            foreground=text_color,
            background=bg_color,
        )
        finish_label.pack(fill=tk.X, pady=2)
        setattr(self, f"player{player_id}_finish_label", finish_label)

        # Breakout Rolls
        breakout_label = ttk.Label(
            stats_frame,
            text="",
            font=("TkDefaultFont", 11),
            foreground=text_color,
            background=bg_color,
        )
        breakout_label.pack(fill=tk.X, pady=2)
        setattr(self, f"player{player_id}_breakout_label", breakout_label)

        # Hand and Deck counts
        counts_label = ttk.Label(
            stats_frame,
            text="Hand: 0  Deck: 30",
            font=("TkDefaultFont", 11),
            foreground=text_color,
            background=bg_color,
        )
        counts_label.pack(fill=tk.X, pady=2)
        setattr(self, f"player{player_id}_counts_label", counts_label)

        # Turns Passed
        passed_label = ttk.Label(
            stats_frame,
            text="Turns Passed: 0",
            font=("TkDefaultFont", 11),
            foreground=text_color,
            background=bg_color,
        )
        passed_label.pack(fill=tk.X, pady=2)
        setattr(self, f"player{player_id}_passed_label", passed_label)

        # Phase 2: In-play and Discard sections would go here

        return frame

    # ==================== Update Methods ====================

    def update_match_title(self, title: str) -> None:
        """Update match title."""
        self.title_label.config(text=title if title else "No match started")

    def update_match_stipulations(self, stipulations: str) -> None:
        """Update match stipulations."""
        if stipulations:
            self.stipulations_label.config(text=f"| {stipulations}")
        else:
            self.stipulations_label.config(text="")

    def update_crowd_meter(self, value: int) -> None:
        """Update crowd meter display."""
        meter_str = render_crowd_meter(value)
        self.crowd_label.config(text=f"Crowd: {meter_str}")

    def update_player_competitor(self, player_id: int, competitor_card: Card | None) -> None:
        """
        Update player competitor image.

        Args:
            player_id: Player ID (1 or 2)
            competitor_card: Competitor card or None
        """
        self.player_data[player_id]["competitor_card"] = competitor_card

        img_label = getattr(self, f"player{player_id}_img_label")

        if competitor_card:
            # Load competitor image (200x280px for expanded view)
            photo = load_competitor_image(competitor_card.db_uuid, (200, 280), self.images_path)
            if photo:
                img_label.config(image=photo)
                img_label.image = photo  # Keep reference
        else:
            img_label.config(image="")

    def update_player_state(self, player_id: int) -> None:
        """
        Update all player state displays.

        Args:
            player_id: Player ID (1 or 2)
        """
        state = self.player_data[player_id]["state"]

        # Update roll display
        roll_label = getattr(self, f"player{player_id}_roll_label")
        type_text, value_text = format_roll_display(state.last_turn_roll)

        if type_text and value_text:
            # Get color for roll type
            roll_color = get_roll_color(state.last_turn_roll.roll_type, self.config)
            roll_label.config(text=f"{type_text} {value_text}", foreground=roll_color)
        else:
            roll_label.config(text="No roll yet", foreground=self.config.production_ui.text_color)

        # Update finish roll
        finish_label = getattr(self, f"player{player_id}_finish_label")
        if state.finish_roll is not None:
            finish_label.config(text=f"Finish Roll: {state.finish_roll}")
        else:
            finish_label.config(text="")

        # Update breakout rolls
        breakout_label = getattr(self, f"player{player_id}_breakout_label")
        if state.breakout_rolls:
            rolls_str = ", ".join(str(r) for r in state.breakout_rolls)
            breakout_label.config(text=f"Breakout: {rolls_str}")
        else:
            breakout_label.config(text="")

        # Update counts
        counts_label = getattr(self, f"player{player_id}_counts_label")
        counts_label.config(text=f"Hand: {state.hand_count}  Deck: {state.deck_count}")

        # Update turns passed
        passed_label = getattr(self, f"player{player_id}_passed_label")
        passed_label.config(text=f"Turns Passed: {state.turns_passed}")

    def update_player_hand_count(self, player_id: int, count: int) -> None:
        """Update player hand count."""
        self.player_data[player_id]["state"].hand_count = count
        self.update_player_state(player_id)

    def update_player_deck_count(self, player_id: int, count: int) -> None:
        """Update player deck count."""
        self.player_data[player_id]["state"].deck_count = count
        self.update_player_state(player_id)

    def update_player_turn_roll(self, player_id: int, roll_type: RollType, value: int) -> None:
        """Update player turn roll."""
        from ...shared.models import TurnRoll

        self.player_data[player_id]["state"].last_turn_roll = TurnRoll(
            roll_type=roll_type, value=value
        )
        self.update_player_state(player_id)

    def update_player_turns_passed(self, player_id: int, count: int) -> None:
        """Update player turns passed."""
        self.player_data[player_id]["state"].turns_passed = count
        self.update_player_state(player_id)

    def update_player_finish_roll(self, player_id: int, value: int | None) -> None:
        """Update player finish roll."""
        self.player_data[player_id]["state"].finish_roll = value
        self.update_player_state(player_id)

    def update_player_breakout_rolls(self, player_id: int, rolls: list[int]) -> None:
        """Update player breakout rolls."""
        self.player_data[player_id]["state"].breakout_rolls = rolls
        self.update_player_state(player_id)
