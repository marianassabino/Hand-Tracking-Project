# effect_map.py
import voicemeeterlib
import midi_out
from config import (
    VOICEMEETER_STRIP, MIDI_CHANNEL,
    VALHALLA_MIX_CC, VALHALLA_SIZE_CC,
    VOCODER_CARRIER_CC, VOCODER_FORMANT_CC,
    PITCH_GAIN_RANGE,
)

_vm = None

def init_voicemeeter():
    global _vm
    _vm = voicemeeterlib.api("banana")
    _vm.login()
    print("[effect_map] VoiceMeeter connected.")

def shutdown_voicemeeter():
    if _vm:
        _vm.logout()

def apply(state: dict) -> dict:
    """
    Translate gesture state → audio effects.
    Returns a flat dict of applied values for HUD display.
    """
    lh = state.get("left",  {})
    rh = state.get("right", {})
    applied = {}

    # --- Mute logic: L open palm + R fist simultaneously ---
    mute = (lh.get("gesture") == "open_palm" and
            rh.get("gesture") == "fist")
    if _vm:
        _vm.strip[VOICEMEETER_STRIP].mute = mute
    applied["mute"] = mute

    if not mute:
        # --- Left hand: wrist height → Valhalla reverb mix ---
        reverb_mix = lh.get("wrist_y", 0.5)
        midi_out.send_cc(MIDI_CHANNEL, VALHALLA_MIX_CC, reverb_mix)
        applied["reverb_mix"] = reverb_mix

        # --- Left hand: spread → reverb size ---
        reverb_size = lh.get("spread", 0.0)
        midi_out.send_cc(MIDI_CHANNEL, VALHALLA_SIZE_CC, reverb_size)
        applied["reverb_size"] = reverb_size

        # --- Right hand: pinch → vocoder carrier amount ---
        carrier = rh.get("pinch", 0.0)
        midi_out.send_cc(MIDI_CHANNEL, VOCODER_CARRIER_CC, carrier)
        applied["carrier"] = carrier

        # --- Right hand: wrist height → pitch (VoiceMeeter gain) ---
        pitch_norm = rh.get("wrist_y", 0.5)           # 0.0–1.0
        gain_db = (pitch_norm - 0.5) * 2 * PITCH_GAIN_RANGE  # ±6 dB
        if _vm:
            _vm.strip[VOICEMEETER_STRIP].gain = gain_db
        applied["pitch_db"] = round(gain_db, 1)

    return applied