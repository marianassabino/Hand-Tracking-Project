# config.py
# Single source of truth for all tunable values in SoundGloves.
# Edit these numbers to tune the feel of your gloves.

MIDI_CHANNEL        = 1       # 1-indexed MIDI channel

# ── Valhalla Future Verb CC assignments ───────────────────────────────────────
# Right-click each knob in Valhalla → MIDI Learn to confirm these
VALHALLA_MIX_CC     = 93      # dry/wet mix
VALHALLA_SIZE_CC    = 91      # reverb size / room size

# ── TAL-Vocoder CC assignments ────────────────────────────────────────────────
VOCODER_CARRIER_CC  = 74      # carrier/effect amount
VOCODER_FORMANT_CC  = 71      # formant shift

# ── Pitch CC ──────────────────────────────────────────────────────────────────
# Assign this in Reaper to a pitch shift plugin parameter
PITCH_CC            = 73

# ── Mute ──────────────────────────────────────────────────────────────────────
# Uses CC 7 (MIDI volume) — map in Reaper to the track volume fader
MUTE_CC             = 7

# ── Gesture sensitivity thresholds (0.0–1.0, normalized screen coords) ────────
PINCH_CLOSED        = 0.04    # distance below this = fully pinched
PINCH_OPEN          = 0.18    # distance above this = fully open
SPREAD_MIN          = 0.10    # min spread (fist)
SPREAD_MAX          = 0.45    # max spread (open palm)

# ── Smoothing ─────────────────────────────────────────────────────────────────
# Higher = more lag but less jitter (0.0–1.0)
SMOOTH_ALPHA        = 0.25