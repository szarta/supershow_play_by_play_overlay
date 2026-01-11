"""
Player state UI component.

Reusable widget for displaying and controlling player state (turn roll, hand/deck counts, turns).
"""

import tkinter as tk
from collections.abc import Callable
from tkinter import messagebox, ttk

from ...shared.models import PlayerState, RollType


class PlayerFrame(ttk.LabelFrame):
    """Reusable player state widget."""

    def __init__(
        self,
        parent,
        player_id: int,
        on_update_roll: Callable[[int, RollType, int], None],
        on_increment_hand: Callable[[int], None],
        on_decrement_hand: Callable[[int], None],
        on_update_finish_roll: Callable[[int, int | None], None],
        on_add_breakout_roll: Callable[[int, int], None],
        on_clear_breakout_rolls: Callable[[int], None],
        on_increment_turns_passed: Callable[[int], None],
    ):
        """
        Initialize the player frame.

        Args:
            parent: Parent widget
            player_id: Player ID (1 or 2)
            on_update_roll: Callback for turn roll updates (player_id, roll_type, value)
            on_increment_hand: Callback for hand count increment (player_id)
            on_decrement_hand: Callback for hand count decrement (player_id)
            on_update_finish_roll: Callback for finish roll update (player_id, value)
            on_add_breakout_roll: Callback for adding breakout roll (player_id, value)
            on_clear_breakout_rolls: Callback for clearing breakout rolls (player_id)
            on_increment_turns_passed: Callback for turns passed increment (player_id)
        """
        super().__init__(parent, text=f"Player {player_id}")
        self.player_id = player_id

        # Callbacks
        self.on_update_roll = on_update_roll
        self.on_increment_hand = on_increment_hand
        self.on_decrement_hand = on_decrement_hand
        self.on_update_finish_roll = on_update_finish_roll
        self.on_add_breakout_roll = on_add_breakout_roll
        self.on_clear_breakout_rolls = on_clear_breakout_rolls
        self.on_increment_turns_passed = on_increment_turns_passed

        # Variables for UI state
        self.roll_type_var = tk.StringVar(value="Power")
        self.roll_value_var = tk.IntVar(value=6)
        self.hand_count_var = tk.StringVar(value="0")
        self.deck_count_var = tk.StringVar(value="30")
        self.turns_passed_var = tk.StringVar(value="0")
        self.finish_roll_var = tk.IntVar(value=6)
        self.breakout_roll_var = tk.IntVar(value=6)
        self.breakout_rolls_display_var = tk.StringVar(value="None")

        self._create_widgets()

    def _create_widgets(self) -> None:
        """Create all widgets for the player frame."""
        # Turn Roll Section
        roll_frame = ttk.LabelFrame(self, text="Turn Roll")
        roll_frame.pack(fill=tk.X, padx=5, pady=5)

        # Roll type row
        type_row = ttk.Frame(roll_frame)
        type_row.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(type_row, text="Type:").pack(side=tk.LEFT)
        roll_type_combo = ttk.Combobox(
            type_row,
            textvariable=self.roll_type_var,
            values=["Power", "Technique", "Agility"],
            state="readonly",
            width=12,
        )
        roll_type_combo.pack(side=tk.LEFT, padx=5)

        # Roll value row
        value_row = ttk.Frame(roll_frame)
        value_row.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(value_row, text="Value:").pack(side=tk.LEFT)
        roll_value_spin = ttk.Spinbox(
            value_row, textvariable=self.roll_value_var, from_=1, to=12, width=5
        )
        roll_value_spin.pack(side=tk.LEFT, padx=5)

        # Update roll button
        update_roll_btn = ttk.Button(
            roll_frame, text="Update Roll", command=self._handle_update_roll
        )
        update_roll_btn.pack(pady=5)

        # Hand Count Section
        hand_frame = ttk.LabelFrame(self, text="Hand Count")
        hand_frame.pack(fill=tk.X, padx=5, pady=5)

        hand_controls = ttk.Frame(hand_frame)
        hand_controls.pack(pady=5)

        ttk.Button(hand_controls, text="-", command=self._handle_decrement_hand, width=3).pack(
            side=tk.LEFT, padx=2
        )

        hand_label = ttk.Label(
            hand_controls,
            textvariable=self.hand_count_var,
            font=("TkDefaultFont", 16, "bold"),
            width=4,
        )
        hand_label.pack(side=tk.LEFT, padx=10)

        ttk.Button(hand_controls, text="+", command=self._handle_increment_hand, width=3).pack(
            side=tk.LEFT, padx=2
        )

        # Deck Count Section (read-only)
        deck_frame = ttk.LabelFrame(self, text="Deck Count")
        deck_frame.pack(fill=tk.X, padx=5, pady=5)

        deck_label = ttk.Label(
            deck_frame,
            textvariable=self.deck_count_var,
            font=("TkDefaultFont", 16),
            anchor=tk.CENTER,
        )
        deck_label.pack(pady=5)

        # Finish Roll Section
        finish_roll_frame = ttk.LabelFrame(self, text="Finish Roll")
        finish_roll_frame.pack(fill=tk.X, padx=5, pady=5)

        finish_roll_controls = ttk.Frame(finish_roll_frame)
        finish_roll_controls.pack(pady=5)

        ttk.Label(finish_roll_controls, text="Value:").pack(side=tk.LEFT)
        finish_roll_spin = ttk.Spinbox(
            finish_roll_controls, textvariable=self.finish_roll_var, from_=1, to=12, width=5
        )
        finish_roll_spin.pack(side=tk.LEFT, padx=5)

        ttk.Button(
            finish_roll_controls, text="Set Finish", command=self._handle_set_finish_roll
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(finish_roll_controls, text="Clear", command=self._handle_clear_finish_roll).pack(
            side=tk.LEFT, padx=2
        )

        # Breakout Rolls Section
        breakout_frame = ttk.LabelFrame(self, text="Breakout Rolls")
        breakout_frame.pack(fill=tk.X, padx=5, pady=5)

        breakout_controls = ttk.Frame(breakout_frame)
        breakout_controls.pack(pady=5)

        ttk.Label(breakout_controls, text="Value:").pack(side=tk.LEFT)
        breakout_roll_spin = ttk.Spinbox(
            breakout_controls, textvariable=self.breakout_roll_var, from_=1, to=12, width=5
        )
        breakout_roll_spin.pack(side=tk.LEFT, padx=5)

        ttk.Button(breakout_controls, text="Add Roll", command=self._handle_add_breakout_roll).pack(
            side=tk.LEFT, padx=2
        )

        ttk.Button(
            breakout_controls, text="Clear All", command=self._handle_clear_breakout_rolls
        ).pack(side=tk.LEFT, padx=2)

        # Display breakout rolls
        ttk.Label(
            breakout_frame, textvariable=self.breakout_rolls_display_var, font=("TkDefaultFont", 10)
        ).pack(pady=2)

        # Turns Passed Section
        turns_passed_frame = ttk.LabelFrame(self, text="Turns Passed")
        turns_passed_frame.pack(fill=tk.X, padx=5, pady=5)

        turns_passed_display = ttk.Frame(turns_passed_frame)
        turns_passed_display.pack(pady=5)

        ttk.Label(
            turns_passed_display, textvariable=self.turns_passed_var, font=("TkDefaultFont", 14)
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            turns_passed_display, text="+1 Turn Passed", command=self._handle_increment_turns_passed
        ).pack(side=tk.LEFT, padx=5)

    def _handle_update_roll(self) -> None:
        """Handle update roll button click."""
        try:
            roll_type_str = self.roll_type_var.get()
            roll_value = self.roll_value_var.get()

            # Validate
            if not (1 <= roll_value <= 12):
                messagebox.showerror("Invalid Roll", "Roll value must be between 1 and 12")
                return

            # Convert string to RollType enum
            roll_type = RollType(roll_type_str.upper())

            # Call callback
            self.on_update_roll(self.player_id, roll_type, roll_value)

        except ValueError as e:
            messagebox.showerror("Error", f"Invalid roll type: {e}")

    def _handle_increment_hand(self) -> None:
        """Handle hand count increment."""
        self.on_increment_hand(self.player_id)

    def _handle_decrement_hand(self) -> None:
        """Handle hand count decrement."""
        self.on_decrement_hand(self.player_id)

    def _handle_set_finish_roll(self) -> None:
        """Handle setting finish roll."""
        value = self.finish_roll_var.get()
        self.on_update_finish_roll(self.player_id, value)

    def _handle_clear_finish_roll(self) -> None:
        """Handle clearing finish roll."""
        self.on_update_finish_roll(self.player_id, None)

    def _handle_add_breakout_roll(self) -> None:
        """Handle adding a breakout roll."""
        value = self.breakout_roll_var.get()
        self.on_add_breakout_roll(self.player_id, value)

    def _handle_clear_breakout_rolls(self) -> None:
        """Handle clearing all breakout rolls."""
        self.on_clear_breakout_rolls(self.player_id)

    def _handle_increment_turns_passed(self) -> None:
        """Handle turns passed increment."""
        self.on_increment_turns_passed(self.player_id)

    def update_display(self, player_state: PlayerState) -> None:
        """
        Update the display with player state.

        Args:
            player_state: Current player state
        """
        self.hand_count_var.set(str(player_state.hand_count))
        self.deck_count_var.set(str(player_state.deck_count))
        self.turns_passed_var.set(str(player_state.turns_passed))

        # Update roll display if available
        if player_state.last_turn_roll:
            self.roll_type_var.set(player_state.last_turn_roll.roll_type.value.capitalize())
            self.roll_value_var.set(player_state.last_turn_roll.value)

        # Update finish roll display
        if player_state.finish_roll is not None:
            self.finish_roll_var.set(player_state.finish_roll)

        # Update breakout rolls display
        if player_state.breakout_rolls:
            rolls_str = ", ".join(str(r) for r in player_state.breakout_rolls)
            self.breakout_rolls_display_var.set(f"Rolls: {rolls_str}")
        else:
            self.breakout_rolls_display_var.set("None")
