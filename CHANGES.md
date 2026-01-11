# Controller Changes - 2026-01-11

## Summary

Updated the controller to remove turns won tracking and add finish/breakout roll features, plus a quit button.

## Changes Made

### 1. **Removed Turns Won Tracking**
- Removed `turns_won` field from `PlayerState` model
- Removed `PLAYER_TURNS_WON` MQTT topic
- Removed turns won UI section from PlayerFrame
- Removed `publish_player_turns_won()` from publisher
- Removed `increment_turns_won()` from controller

**Rationale:** Turns won can be inferred from turn rolls and card play in the match recording.

### 2. **Added Finish Roll Tracking**
- Added `finish_roll: int | None` field to `PlayerState` model
- Added `PLAYER_FINISH_ROLL` MQTT topic (`supershow/player/{player_id}/finish_roll`)
- Added finish roll UI section to PlayerFrame:
  - Value spinbox (1-12)
  - "Set Finish" button
  - "Clear" button
- Added `publish_player_finish_roll()` to publisher
- Added `update_finish_roll()` to controller

**Usage:** When a player lands a finish, enter the finish roll value and click "Set Finish".

### 3. **Added Breakout Rolls Tracking**
- Added `breakout_rolls: list[int]` field to `PlayerState` model
- Added `PLAYER_BREAKOUT_ROLLS` MQTT topic (`supershow/player/{player_id}/breakout_rolls`)
- Added breakout rolls UI section to PlayerFrame:
  - Value spinbox (1-12)
  - "Add Roll" button
  - "Clear All" button
  - Display showing current rolls (e.g., "Rolls: 4, 8, 11")
- Added `publish_player_breakout_rolls()` to publisher
- Added `add_breakout_roll()` and `clear_breakout_rolls()` to controller

**Usage:** When a player needs to make breakout rolls, enter each roll value and click "Add Roll". Click "Clear All" when done.

### 4. **Added Quit Button**
- Added "Quit" button to match setup frame (right side)
- Button calls `root.quit()` to close the application cleanly

## Files Modified

### Models & MQTT
- `src/shared/models.py` - Updated PlayerState
- `src/shared/mqtt_client.py` - Updated Topics class

### Controller Logic
- `src/controller/publisher.py` - Updated publish methods
- `src/controller/controller.py` - Updated state management methods

### UI Components
- `src/controller/ui/player_frame.py` - Updated player UI controls
- `src/controller/ui/match_setup_frame.py` - Added quit button
- `src/controller/ui/main_window.py` - Updated callbacks

## MQTT Topics

### New Topics
- `supershow/player/{1,2}/finish_roll` - Integer (1-12) or empty string
- `supershow/player/{1,2}/breakout_rolls` - Array of integers

### Removed Topics
- `supershow/player/{1,2}/turns_won` - No longer published

## UI Layout Changes

### Player Frame (Before)
```
Turn Roll
Hand Count
Deck Count
Turns Won      ← REMOVED
Turns Passed
```

### Player Frame (After)
```
Turn Roll
Hand Count
Deck Count
Finish Roll    ← NEW
Breakout Rolls ← NEW
Turns Passed
```

### Match Setup Frame
```
[Start Match] [Reset Match] [Quit]  ← Quit button added
```

## Testing

All changes tested:
- ✅ Controller launches successfully
- ✅ Linting passes (26 issues auto-fixed)
- ✅ MQTT connectivity working
- ✅ Database loaded (1,094 competitors)

## Next Steps

When implementing the production view:
- Subscribe to `finish_roll` and `breakout_rolls` topics
- Display finish roll prominently when set
- Display breakout rolls list when populated
- Clear displays when values are cleared/reset
