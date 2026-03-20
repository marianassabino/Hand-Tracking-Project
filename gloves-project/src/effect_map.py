# effect_map.py
# Translates gesture state → MIDI CC messages via LoopMIDI → Reaper
# No VoiceMeeter dependency — everything goes through MIDI now.

import midi_out
from config import (
    MIDI_CHANNEL,
    VALHALLA_MIX_CC,
    VALHALLA_SIZE_CC,
    VOCODER_CARRIER_CC,
    VOCODER_FORMANT_CC,
    PITCH_CC,
)


def init():
    """Call once at startup — just confirms MIDI is ready."""
    print("[effect_map] Ready — all effects via MIDI CC over LoopMIDI.")


def shutdown():
    """Call on exit."""
    pass  # nothing to close here — midi_out.close() handles it


def apply(state: dict) -> dict:
    """
    Translate gesture state → MIDI CC messages.
    Returns a flat dict of applied values for HUD display.
    """
    lh = state.get("left",  {})
    rh = state.get("right", {})
    applied = {}

    # --- Mute: L open palm + R fist simultaneously ---
    # We send CC 7 (volume) to 0 as a mute substitute
    mute = (lh.get("gesture") == "open_palm" and
            rh.get("gesture") == "fist")
    midi_out.send_cc(MIDI_CHANNEL, 7, 0.0 if mute else 1.0)
    applied["mute"] = mute

    if not mute:
        # --- Left wrist height → Valhalla reverb mix ---
        reverb_mix = lh.get("wrist_y", 0.5)
        midi_out.send_cc(MIDI_CHANNEL, VALHALLA_MIX_CC, reverb_mix)
        applied["reverb_mix"] = reverb_mix

        # --- Left finger spread → Valhalla reverb size ---
        reverb_size = lh.get("spread", 0.0)
        midi_out.send_cc(MIDI_CHANNEL, VALHALLA_SIZE_CC, reverb_size)
        applied["reverb_size"] = reverb_size

        # --- Right pinch → TAL-Vocoder carrier amount ---
        carrier = rh.get("pinch", 0.0)
        midi_out.send_cc(MIDI_CHANNEL, VOCODER_CARRIER_CC, carrier)
        applied["carrier"] = carrier

        # --- Right wrist height → pitch (MIDI CC to a pitch plugin or Reaper param) ---
        pitch = rh.get("wrist_y", 0.5)
        midi_out.send_cc(MIDI_CHANNEL, PITCH_CC, pitch)
        applied["pitch"] = pitch

    return applied