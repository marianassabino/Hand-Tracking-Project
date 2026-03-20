# config.py

VOICEMEETER_STRIP = 0        # which strip your mic is on (0-indexed)
MIDI_CHANNEL      = 1        # 1-indexed MIDI channel

# Valhalla Future Verb CC assignments (right-click any knob → Learn MIDI CC)
VALHALLA_MIX_CC   = 93
VALHALLA_SIZE_CC  = 91
VALHALLA_PREDELAY_CC = 78

# TAL-Vocoder CC assignments
VOCODER_CARRIER_CC = 74
VOCODER_FORMANT_CC = 71

# Gesture sensitivity thresholds (0.0–1.0, normalized screen coords)
PINCH_CLOSED      = 0.04    # distance below this = fully pinched
PINCH_OPEN        = 0.18    # distance above this = fully open
SPREAD_MIN        = 0.10    # min spread value (fist)
SPREAD_MAX        = 0.45    # max spread value (open palm)

# Smoothing: higher = more lag but less jitter (0.0–1.0)
SMOOTH_ALPHA      = 0.25

# VoiceMeeter pitch range
PITCH_GAIN_RANGE  = 6.0     # ±dB