"""
Collapsed view for production overlay.

Displays minimal bottom bar with match info and player summaries.
"""

import logging
import tkinter as tk
from collections.abc import Callable
from pathlib import Path
from tkinter import ttk

from ...shared.config import Config
from ...shared.models import Card, PlayerState, RollType
from .utils import (
    format_breakout_rolls,
    format_finish_roll,
    format_roll_display,
    get_roll_color,
    load_competitor_image,
    render_crowd_meter,
)

logger = logging.getLogger(__name__)


class CollapsedView(ttk.Frame):
    """Minimal collapsed view (1920x150px by default)."""

    def __init__(
        self,
        parent: tk.Widget,
        config: Config,
        on_player_click: Callable[[int], None],
    ):
        """
        Initialize collapsed view.

        Args:
            parent: Parent widget
            config: Configuration
            on_player_click: Callback when player section is clicked (player_id)
        """
        super().__init__(parent)
        self.config = config
        self.on_player_click = on_player_click
        self.images_path = Path(config.database.images_path)

        # Player state tracking
        self.player_data = {
            1: {"competitor_card": None, "state": PlayerState(player_id=1)},
            2: {"competitor_card": None, "state": PlayerState(player_id=2)},
        }

        # Create widgets
        self._create_widgets()

    def _create_widgets(self) -> None:
        """Create all widgets for collapsed view."""
        # Configure background
        bg_color = self.config.production_ui.background_color
        text_color = self.config.production_ui.text_color

        self.configure(style="Collapsed.TFrame")

        # Top bar - Match Info
        top_frame = ttk.Frame(self, style="Collapsed.TFrame")
        top_frame.pack(fill=tk.X, pady=(5, 0))

        self.title_label = ttk.Label(
            top_frame,
            text="No match started",
            font=("TkDefaultFont", 14, "bold"),
            foreground=text_color,
            background=bg_color,
        )
        self.title_label.pack(side=tk.LEFT, padx=10)

        self.stipulations_label = ttk.Label(
            top_frame,
            text="",
            font=("TkDefaultFont", 12),
            foreground=text_color,
            background=bg_color,
        )
        self.stipulations_label.pack(side=tk.LEFT, padx=10)

        self.crowd_label = ttk.Label(
            top_frame,
            text="Crowd: ○○○○○○○○○○",
            font=("TkDefaultFont", 12),
            foreground=text_color,
            background=bg_color,
        )
        self.crowd_label.pack(side=tk.RIGHT, padx=10)

        # Separator
        ttk.Separator(self, orient="horizontal").pack(fill=tk.X, pady=5)

        # Player sections (side by side)
        players_frame = ttk.Frame(self, style="Collapsed.TFrame")
        players_frame.pack(fill=tk.BOTH, expand=True)

        # Player 1 (left side)
        self.player1_frame = self._create_player_panel(players_frame, 1)
        self.player1_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        # Center spacer
        ttk.Frame(players_frame, width=20, style="Collapsed.TFrame").pack(side=tk.LEFT)

        # Player 2 (right side)
        self.player2_frame = self._create_player_panel(players_frame, 2)
        self.player2_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

    def _create_player_panel(self, parent: tk.Widget, player_id: int) -> ttk.Frame:
        """
        Create player panel with competitor image and stats.

        Args:
            parent: Parent widget
            player_id: Player ID (1 or 2)

        Returns:
            Player panel frame
        """
        bg_color = self.config.production_ui.background_color
        text_color = self.config.production_ui.text_color

        # Main frame (clickable)
        frame = ttk.Frame(parent, style="Collapsed.TFrame", relief=tk.RAISED, borderwidth=2)

        # Bind click to expand
        frame.bind("<Button-1>", lambda e: self.on_player_click(player_id))

        # Header
        header = ttk.Label(
            frame,
            text=f"Player {player_id}",
            font=("TkDefaultFont", 12, "bold"),
            foreground=text_color,
            background=bg_color,
        )
        header.pack(pady=5)
        header.bind("<Button-1>", lambda e: self.on_player_click(player_id))

        # Competitor image
        img_label = ttk.Label(frame, background=bg_color)
        img_label.pack(pady=5)
        img_label.bind("<Button-1>", lambda e: self.on_player_click(player_id))

        # Store reference
        setattr(self, f"player{player_id}_img_label", img_label)

        # Stats labels
        stats_frame = ttk.Frame(frame, style="Collapsed.TFrame")
        stats_frame.pack(fill=tk.X, pady=5)
        stats_frame.bind("<Button-1>", lambda e: self.on_player_click(player_id))

        # Roll label (colored)
        roll_label = ttk.Label(
            stats_frame,
            text="",
            font=("TkDefaultFont", 11),
            foreground=text_color,
            background=bg_color,
        )
        roll_label.pack()
        roll_label.bind("<Button-1>", lambda e: self.on_player_click(player_id))
        setattr(self, f"player{player_id}_roll_label", roll_label)

        # Hand/Deck counts
        counts_label = ttk.Label(
            stats_frame,
            text="H:0  D:30",
            font=("TkDefaultFont", 10),
            foreground=text_color,
            background=bg_color,
        )
        counts_label.pack()
        counts_label.bind("<Button-1>", lambda e: self.on_player_click(player_id))
        setattr(self, f"player{player_id}_counts_label", counts_label)

        # Finish/Breakout label
        finish_label = ttk.Label(
            stats_frame,
            text="",
            font=("TkDefaultFont", 10),
            foreground=text_color,
            background=bg_color,
        )
        finish_label.pack()
        finish_label.bind("<Button-1>", lambda e: self.on_player_click(player_id))
        setattr(self, f"player{player_id}_finish_label", finish_label)

        # Turns passed / In-play/Discard counts
        misc_label = ttk.Label(
            stats_frame,
            text="P:0",
            font=("TkDefaultFont", 10),
            foreground=text_color,
            background=bg_color,
        )
        misc_label.pack()
        misc_label.bind("<Button-1>", lambda e: self.on_player_click(player_id))
        setattr(self, f"player{player_id}_misc_label", misc_label)

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
            # Load competitor image (60x84px thumbnail)
            photo = load_competitor_image(competitor_card.db_uuid, (60, 84), self.images_path)
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
            roll_label.config(text=f"{type_text}:{value_text}", foreground=roll_color)
        else:
            roll_label.config(text="No roll", foreground=self.config.production_ui.text_color)

        # Update counts
        counts_label = getattr(self, f"player{player_id}_counts_label")
        counts_label.config(text=f"H:{state.hand_count}  D:{state.deck_count}")

        # Update finish/breakout
        finish_label = getattr(self, f"player{player_id}_finish_label")
        finish_text = format_finish_roll(state.finish_roll)
        breakout_text = format_breakout_rolls(state.breakout_rolls)

        # Combine finish and breakout
        combined = []
        if finish_text:
            combined.append(finish_text)
        if breakout_text:
            combined.append(breakout_text)

        finish_label.config(text="  ".join(combined))

        # Update misc (turns passed, in-play/discard counts)
        misc_label = getattr(self, f"player{player_id}_misc_label")
        misc_parts = [f"P:{state.turns_passed}"]

        # Phase 2: Add in-play and discard counts
        if state.in_play:
            misc_parts.append(f"Play:{len(state.in_play)}")
        if state.discard_pile:
            misc_parts.append(f"Disc:{len(state.discard_pile)}")

        misc_label.config(text="  ".join(misc_parts))

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
