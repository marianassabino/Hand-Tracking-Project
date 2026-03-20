# midi_out.py
import rtmidi

_midiout = rtmidi.MidiOut()
_port_index: int | None = None

def connect(port_name_fragment: str = "loopMIDI") -> bool:
    """Open the first LoopMIDI port found. Returns True on success."""
    global _port_index
    ports = _midiout.get_ports()
    for i, name in enumerate(ports):
        if port_name_fragment.lower() in name.lower():
            _midiout.open_port(i)
            _port_index = i
            print(f"[midi_out] Connected to: {name}")
            return True
    print(f"[midi_out] No port matching '{port_name_fragment}' found.")
    print(f"[midi_out] Available ports: {ports}")
    return False

def send_cc(channel: int, cc: int, value: float) -> None:
    """
    Send a MIDI CC message.
    channel: 1–16
    cc:      0–127
    value:   0.0–1.0  (scaled to 0–127 internally)
    """
    if _port_index is None:
        return
    int_val = max(0, min(127, int(value * 127)))
    _midiout.send_message([0xB0 | (channel - 1), cc, int_val])

def close() -> None:
    _midiout.close_port()