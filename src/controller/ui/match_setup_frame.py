"""
Match setup UI component.

Provides controls for setting up a match: title, stipulations, crowd meter,
competitor selection, and match control buttons.
"""

import tkinter as tk
from collections.abc import Callable
from tkinter import messagebox, ttk


class MatchSetupFrame(ttk.LabelFrame):
    """Match setup controls."""

    def __init__(
        self,
        parent,
        competitor_names: list[str],
        on_start_match: Callable,
        on_reset_match: Callable,
        on_quit: Callable,
        on_title_changed: Callable[[str], None],
        on_stipulations_changed: Callable[[str], None],
        on_crowd_meter_changed: Callable[[int], None],
    ):
        """
        Initialize the match setup frame.

        Args:
            parent: Parent widget
            competitor_names: List of competitor names for dropdowns
            on_start_match: Callback for start match button
            on_reset_match: Callback for reset match button
            on_quit: Callback for quit button
            on_title_changed: Callback when title changes
            on_stipulations_changed: Callback when stipulations change
            on_crowd_meter_changed: Callback when crowd meter changes
        """
        super().__init__(parent, text="Match Setup")

        self.competitor_names = competitor_names
        self.on_start_match = on_start_match
        self.on_reset_match = on_reset_match
        self.on_quit = on_quit
        self.on_title_changed = on_title_changed
        self.on_stipulations_changed = on_stipulations_changed
        self.on_crowd_meter_changed = on_crowd_meter_changed

        # Variables for UI state
        self.title_var = tk.StringVar()
        self.stipulations_var = tk.StringVar()
        self.crowd_meter_var = tk.IntVar(value=0)
        self.p1_competitor_var = tk.StringVar()
        self.p2_competitor_var = tk.StringVar()

        # Track if live editing is enabled (after match starts)
        self.live_editing = False

        self._create_widgets()
        self._bind_live_updates()

    def _create_widgets(self) -> None:
        """Create all widgets for the match setup frame."""
        # Title row
        title_row = ttk.Frame(self)
        title_row.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(title_row, text="Title:", width=12).pack(side=tk.LEFT)
        title_entry = ttk.Entry(title_row, textvariable=self.title_var, width=40)
        title_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Stipulations row
        stip_row = ttk.Frame(self)
        stip_row.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(stip_row, text="Stipulations:", width=12).pack(side=tk.LEFT)
        stip_entry = ttk.Entry(stip_row, textvariable=self.stipulations_var, width=40)
        stip_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Crowd meter row
        crowd_row = ttk.Frame(self)
        crowd_row.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(crowd_row, text="Crowd Meter:", width=12).pack(side=tk.LEFT)

        # +/- buttons for crowd meter
        crowd_controls = ttk.Frame(crowd_row)
        crowd_controls.pack(side=tk.LEFT, padx=5)

        ttk.Button(crowd_controls, text="-", command=self._decrement_crowd_meter, width=3).pack(
            side=tk.LEFT, padx=2
        )

        self.crowd_value_label = ttk.Label(
            crowd_controls, textvariable=self.crowd_meter_var, font=("TkDefaultFont", 12), width=3
        )
        self.crowd_value_label.pack(side=tk.LEFT, padx=10)

        ttk.Button(crowd_controls, text="+", command=self._increment_crowd_meter, width=3).pack(
            side=tk.LEFT, padx=2
        )

        # Competitors row
        comp_row = ttk.Frame(self)
        comp_row.pack(fill=tk.X, padx=5, pady=5)

        # Player 1 competitor
        p1_frame = ttk.Frame(comp_row)
        p1_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Label(p1_frame, text="Player 1:").pack(anchor=tk.W)
        p1_combo = ttk.Combobox(
            p1_frame,
            textvariable=self.p1_competitor_var,
            values=self.competitor_names,
            state="normal",
            width=30,
        )
        p1_combo.pack(fill=tk.X)

        # Player 2 competitor
        p2_frame = ttk.Frame(comp_row)
        p2_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Label(p2_frame, text="Player 2:").pack(anchor=tk.W)
        p2_combo = ttk.Combobox(
            p2_frame,
            textvariable=self.p2_competitor_var,
            values=self.competitor_names,
            state="normal",
            width=30,
        )
        p2_combo.pack(fill=tk.X)

        # Control buttons row
        buttons_row = ttk.Frame(self)
        buttons_row.pack(fill=tk.X, padx=5, pady=10)

        self.start_btn = ttk.Button(
            buttons_row, text="Start Match", command=self._handle_start_match
        )
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.reset_btn = ttk.Button(
            buttons_row, text="Reset Match", command=self._handle_reset_match
        )
        self.reset_btn.pack(side=tk.LEFT, padx=5)

        self.quit_btn = ttk.Button(buttons_row, text="Quit", command=self.on_quit)
        self.quit_btn.pack(side=tk.RIGHT, padx=5)

    def _bind_live_updates(self) -> None:
        """Bind variables to trigger live updates after match starts."""
        # We'll manually trigger updates in the callbacks below
        pass

    def _increment_crowd_meter(self) -> None:
        """Increment crowd meter value."""
        current = self.crowd_meter_var.get()
        new_value = min(current + 1, 10)  # Max 10
        self.crowd_meter_var.set(new_value)

        # Trigger callback if live editing is enabled
        if self.live_editing:
            self.on_crowd_meter_changed(new_value)

    def _decrement_crowd_meter(self) -> None:
        """Decrement crowd meter value."""
        current = self.crowd_meter_var.get()
        new_value = max(current - 1, 0)  # Min 0
        self.crowd_meter_var.set(new_value)

        # Trigger callback if live editing is enabled
        if self.live_editing:
            self.on_crowd_meter_changed(new_value)

    def _handle_start_match(self) -> None:
        """Handle start match button click."""
        # Gather input
        title = self.title_var.get().strip()
        stipulations = self.stipulations_var.get().strip()
        p1_name = self.p1_competitor_var.get().strip()
        p2_name = self.p2_competitor_var.get().strip()
        crowd_meter = self.crowd_meter_var.get()

        # Validate
        errors = []
        if not title:
            errors.append("Title is required")
        if not p1_name:
            errors.append("Player 1 competitor is required")
        if not p2_name:
            errors.append("Player 2 competitor is required")

        if errors:
            messagebox.showerror("Cannot Start Match", "\n".join(errors))
            return

        # Call callback with all parameters
        self.on_start_match(title, stipulations, crowd_meter, p1_name, p2_name)

        # Enable live editing
        self.live_editing = True

    def _handle_reset_match(self) -> None:
        """Handle reset match button click."""
        # Call callback
        self.on_reset_match()

        # Reset UI
        self.title_var.set("")
        self.stipulations_var.set("")
        self.crowd_meter_var.set(0)
        self.p1_competitor_var.set("")
        self.p2_competitor_var.set("")

        # Disable live editing
        self.live_editing = False

    def enable_live_editing_callbacks(self) -> None:
        """Enable callbacks for live editing after match start."""

        # Bind Entry widgets to trigger updates on focus out or Enter key
        def on_title_changed(event=None):
            if self.live_editing:
                self.on_title_changed(self.title_var.get())

        def on_stipulations_changed(event=None):
            if self.live_editing:
                self.on_stipulations_changed(self.stipulations_var.get())

        # Find Entry widgets and bind them
        for widget in self.winfo_children():
            if isinstance(widget, ttk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Entry):
                        if child.cget("textvariable") == str(self.title_var):
                            child.bind("<FocusOut>", on_title_changed)
                            child.bind("<Return>", on_title_changed)
                        elif child.cget("textvariable") == str(self.stipulations_var):
                            child.bind("<FocusOut>", on_stipulations_changed)
                            child.bind("<Return>", on_stipulations_changed)

    def get_title(self) -> str:
        """Get current title value."""
        return self.title_var.get()

    def get_stipulations(self) -> str:
        """Get current stipulations value."""
        return self.stipulations_var.get()

    def get_crowd_meter(self) -> int:
        """Get current crowd meter value."""
        return self.crowd_meter_var.get()

    def get_p1_competitor(self) -> str:
        """Get Player 1 competitor name."""
        return self.p1_competitor_var.get()

    def get_p2_competitor(self) -> str:
        """Get Player 2 competitor name."""
        return self.p2_competitor_var.get()
