# Testing MQTT Module

This guide shows how to test the MQTT client module.

## Prerequisites

The MQTT module requires a running MQTT broker. You have several options:

### Option 1: Local Docker Broker (Recommended for Testing)

```bash
# Start Mosquitto broker
docker run -it -p 1883:1883 eclipse-mosquitto:2
```

This starts a broker on `localhost:1883` with no authentication.

### Option 2: Public Test Broker

Update `config.toml` to use a public test broker:

```toml
[mqtt]
broker_host = "test.mosquitto.org"
broker_port = 1883
username = ""
password = ""
```

**Note**: Public brokers are not secure and should only be used for testing.

### Option 3: Install Mosquitto Locally

```bash
# Ubuntu/Debian
sudo apt-get install mosquitto mosquitto-clients

# macOS
brew install mosquitto
brew services start mosquitto

# Test the broker
mosquitto_sub -h localhost -t test &
mosquitto_pub -h localhost -t test -m "Hello"
```

## Running the MQTT Tests

Once you have a broker running, run the example script:

```bash
cd ~/data/overlay_app
python -m src.shared.example_mqtt
```

### Expected Output

```
2024-01-10 12:00:00 - __main__ - INFO - MQTT Client Test Suite
2024-01-10 12:00:00 - __main__ - INFO - ============================================================
2024-01-10 12:00:00 - __main__ - INFO - TESTING TOPIC HELPERS
2024-01-10 12:00:00 - __main__ - INFO - ============================================================
2024-01-10 12:00:00 - __main__ - INFO - Player topic examples:
2024-01-10 12:00:00 - __main__ - INFO -   Player 1 competitor: supershow/player/1/competitor
2024-01-10 12:00:00 - __main__ - INFO -   Player 2 competitor: supershow/player/2/competitor
2024-01-10 12:00:00 - __main__ - INFO -   Player 1 hand count: supershow/player/1/hand_count
...

Do you have a broker running? (y/n): y

2024-01-10 12:00:05 - __main__ - INFO - ============================================================
2024-01-10 12:00:05 - __main__ - INFO - TESTING BASIC PUBLISH/SUBSCRIBE
2024-01-10 12:00:05 - __main__ - INFO - ============================================================
2024-01-10 12:00:05 - mqtt_client - INFO - MQTT client initialized: test_client
2024-01-10 12:00:05 - __main__ - INFO - Connecting to broker...
2024-01-10 12:00:05 - mqtt_client - INFO - Connecting to MQTT broker: localhost:1883
2024-01-10 12:00:06 - mqtt_client - INFO - Connected to MQTT broker
2024-01-10 12:00:06 - __main__ - INFO - ✓ Connected successfully
2024-01-10 12:00:06 - __main__ - INFO - Subscribing to test topic...
2024-01-10 12:00:06 - mqtt_client - INFO - Subscribed to supershow/test
2024-01-10 12:00:06 - __main__ - INFO - Publishing test messages...
2024-01-10 12:00:06 - __main__ - INFO - Received on supershow/test: Hello MQTT!
2024-01-10 12:00:06 - __main__ - INFO - Received on supershow/test: {'type': 'test', 'value': 123}
2024-01-10 12:00:06 - __main__ - INFO - Received 2 messages
2024-01-10 12:00:06 - mqtt_client - INFO - Disconnecting from MQTT broker
...
```

## Testing Match State Publishing

The example script includes a test that simulates the controller/production architecture:

```python
# Controller publishes match init
controller.publish(Topics.MATCH_INIT, {
    "match_id": "test-match-001",
    "title": "Championship Match",
    "stipulations": "New York Rules"
}, qos=1, retain=True)

# Production receives the update
production.subscribe("supershow/match/#", qos=1)
```

This test demonstrates:
- Controller publishing match state updates
- Production view subscribing to all match topics
- Using topic wildcards (`#` and `+`)
- Retained messages for state persistence
- QoS levels for reliable delivery

## Manual Testing with MQTT Clients

You can manually test MQTT topics using command-line tools:

### Subscribe to All Topics

```bash
# Subscribe to all supershow topics
mosquitto_sub -h localhost -t 'supershow/#' -v

# Subscribe to player 1 topics only
mosquitto_sub -h localhost -t 'supershow/player/1/#' -v

# Subscribe to all event topics
mosquitto_sub -h localhost -t 'supershow/events/#' -v
```

### Publish Test Messages

```bash
# Publish match init
mosquitto_pub -h localhost -t 'supershow/match/init' \
  -m '{"match_id":"test","title":"Test Match"}'

# Publish player state
mosquitto_pub -h localhost -t 'supershow/player/1/hand_count' -m '5'

# Publish with retained flag
mosquitto_pub -h localhost -t 'supershow/match/title' \
  -m 'Championship Match' -r

# Publish turn roll event
mosquitto_pub -h localhost -t 'supershow/events/turn_roll' \
  -m '{"player_id":1,"roll_type":"Power","value":8}'
```

## Interactive Python Testing

You can test the MQTT module interactively:

```python
from src.shared.config import Config
from src.shared.mqtt_client import MQTTClient, Topics
import time

# Load config
config = Config("config.toml")

# Create client
client = MQTTClient(
    client_id="test",
    broker_host=config.mqtt.broker_host,
    broker_port=config.mqtt.broker_port
)

# Connect
client.connect()
time.sleep(2)

# Subscribe with handler
def on_message(payload):
    print(f"Received: {payload}")

client.subscribe("supershow/test", handler=on_message)

# Publish
client.publish("supershow/test", "Hello from Python!")

# Wait for message
time.sleep(1)

# Cleanup
client.disconnect()
```

## Testing Topic Formatting

The `Topics` class provides helpers for player-specific topics:

```python
from src.shared.mqtt_client import Topics

# Format player topics
topic = Topics.player_topic(Topics.PLAYER_COMPETITOR, 1)
# Result: "supershow/player/1/competitor"

topic = Topics.player_topic(Topics.PLAYER_HAND_COUNT, 2)
# Result: "supershow/player/2/hand_count"
```

## Troubleshooting

### "Failed to connect to MQTT broker"

**Cause**: Broker is not running or not accessible

**Solutions**:
- Check broker is running: `docker ps` or `systemctl status mosquitto`
- Verify host/port in config.toml
- Check firewall settings
- Try `telnet localhost 1883` to test connectivity

### "Connection failed with code 5"

**Cause**: Authentication failed

**Solutions**:
- Check username/password in config.toml
- Ensure broker allows authentication (or disable it for testing)
- Try connecting without credentials for local testing

### Messages not received

**Causes**:
- Client disconnected before message arrived
- Topic mismatch (check wildcards)
- QoS level too low

**Solutions**:
- Add delays after subscribe: `time.sleep(1)`
- Use QoS 1 or 2 for important messages
- Check topic names match exactly (case-sensitive)
- Use `mosquitto_sub` to verify messages are published

### "Database is locked" errors

**Cause**: Not an MQTT issue - this is a SQLite issue from database module

**Solution**: See `TESTING_SYNC.md` for database troubleshooting

## Testing Retained Messages

Retained messages persist on the broker and are delivered to new subscribers:

```bash
# Publish retained message
mosquitto_pub -h localhost -t 'supershow/match/title' \
  -m 'Championship Match' -r

# Subscribe (will immediately receive retained message)
mosquitto_sub -h localhost -t 'supershow/match/title' -v

# Clear retained message
mosquitto_pub -h localhost -t 'supershow/match/title' -m '' -r -n
```

This is useful for match state that new connections should know about.

## Testing Wildcards

MQTT supports two wildcards:
- `+`: Single level wildcard
- `#`: Multi-level wildcard

```bash
# Subscribe to all player 1 topics
mosquitto_sub -h localhost -t 'supershow/player/1/#' -v

# Subscribe to hand_count for all players
mosquitto_sub -h localhost -t 'supershow/player/+/hand_count' -v

# Subscribe to everything
mosquitto_sub -h localhost -t 'supershow/#' -v
```

## Next Steps

After verifying MQTT works:
1. Build controller app that publishes match state
2. Build production view app that subscribes and displays state
3. Implement match recorder that logs events to JSON
4. Test full system with both apps running
