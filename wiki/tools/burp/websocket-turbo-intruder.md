---
title: WebSocket Turbo Intruder
slug: websocket-turbo-intruder
created_utc: 2026-05-19T00:00:00Z
updated_utc: 2026-05-19T00:00:00Z
tags: [tool/burp, tool/turbo-intruder, technique/websocket, technique/race-conditions]
inbound: []
---

# WebSocket Turbo Intruder

Burp Suite extension for high-speed WebSocket testing. Available from
B-App Store or GitHub. Created by Zach (PortSwigger security associate),
built on the Turbo Intruder core by James Kettle.

## Why it exists
Standard HTTP tools can't properly handle WebSocket's stateful
connections, asynchronous messages, broadcast frames, or protocol
messages (ping/pong/close). WebSocket TI solves all of these.

## Engines
| Engine | Use case |
|--------|----------|
| **Burp** | Standard pen-test; rock-solid, uses Burp's WS stack |
| **Turbo** | Raw frame control; can craft malformed frames (arbitrary opcode + payload_length without actual payload) |
| **Threaded** | Large-scale, brute-force; opens multiple simultaneous WS connections |

## Key features

### Message pairing
Python decorators `HandleOutgoingMessage` / `HandleIncomingMessage` let
you match outgoing frames to their replies and filter broadcast noise.

### HTTP middleware
Wraps WebSocket connections as HTTP POST requests on localhost:9000.
Enables any HTTP-based tool (SQLmap, Burp Scanner) to test WebSocket
endpoints without custom plugins. Right-click a WS message → Extension →
HTTP middleware → select server script → Start Server.

### Race conditions
Use Threaded engine with 10ms send window across multiple threads.
`ping` to warm up connections so frames land simultaneously. Detects
TOCTOU conditions by observing ID/state changes across parallel updates.

### Server-side prototype pollution via Socket.io
Socket.io option `initial_packet` is echoed back on reconnect. Pollute
`Object.prototype.initial_packet` → server echoes attacker-controlled
data on next connection. Confirmation without side effects. Custom Socket.io
handler script included in TI library (handles Engine.io level 4 protocol).

### Malformed frame DoS
Turbo engine can craft: text frame opcode + empty body + giant payload_length
(as string literal since it overflows Python int). Java WebSocket
implementations allocate the buffer before reading payload → OOM → JVM
crash. One tiny packet causes server to stop responding.

### CLI (scylla-i)
Standalone command-line runner for long-running attacks:
```
scylla-i script.py request.bin wss://target.com/ws §placeholder§
```
Results saved to `results.json`.

## Script structure
```python
def queueWebSockets(target, wordlists):
    connection = target.createConnection(engine=Engine.TURBO)
    # ...

def handleOutgoingMessage(conn, message):
    table.add(message)

def handleIncomingMessage(conn, message):
    if interesting(message):
        table.add(message)
```

## Common targets
- WS-based chat/notification systems: brute-force login
- Financial/trading apps: race condition on balance updates
- Socket.io apps: SSPP detection via initial_packet gadget
- Base64-encoded WS message apps: use b64-encode temper script → SQLmap

## References
- PortSwigger TV: "WebSocket Turbo Intruder for Burp Suite" — Zach
  — `wiki/sources/portswigger-tv/whisper/transcripts/q-TWZ24A7dw_*.txt`
- GitHub: PortSwigger/websocket-turbo-intruder
- Related: [[turbo-intruder-anomaly-rank]], [[websocket-testing]]
