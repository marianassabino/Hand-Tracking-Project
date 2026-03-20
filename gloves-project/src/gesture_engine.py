# gesture_engine.py
import math
from config import (
    PINCH_CLOSED, PINCH_OPEN,
    SPREAD_MIN, SPREAD_MAX,
    SMOOTH_ALPHA
)

# Landmark indices (MediaPipe hand)
WRIST       = 0
THUMB_TIP   = 4
INDEX_TIP   = 8
MIDDLE_TIP  = 12
RING_TIP    = 16
PINKY_TIP   = 20
INDEX_MCP   = 5   # knuckle — used for spread baseline

_smooth_state: dict[str, float] = {}

def _smooth(key: str, value: float) -> float:
    prev = _smooth_state.get(key, value)
    smoothed = SMOOTH_ALPHA * value + (1 - SMOOTH_ALPHA) * prev
    _smooth_state[key] = smoothed
    return smoothed

def _dist(a, b) -> float:
    return math.hypot(a.x - b.x, a.y - b.y)

def _normalize(value: float, lo: float, hi: float) -> float:
    return max(0.0, min(1.0, (value - lo) / (hi - lo)))

def _wrist_y(lm) -> float:
    """0.0 = bottom of frame, 1.0 = top (inverted from MediaPipe's y)."""
    return 1.0 - lm[WRIST].y

def _pinch(lm) -> float:
    """0.0 = fully pinched, 1.0 = fully open."""
    d = _dist(lm[THUMB_TIP], lm[INDEX_TIP])
    return _normalize(d, PINCH_CLOSED, PINCH_OPEN)

def _spread(lm) -> float:
    """0.0 = fist, 1.0 = fully spread."""
    tip_ids = [INDEX_TIP, MIDDLE_TIP, RING_TIP, PINKY_TIP]
    max_spread = max(_dist(lm[t], lm[INDEX_MCP]) for t in tip_ids)
    return _normalize(max_spread, SPREAD_MIN, SPREAD_MAX)

def _is_fist(lm) -> bool:
    """True when all four fingertips are below their MCP knuckles."""
    pairs = [(8,5), (12,9), (16,13), (20,17)]
    return all(lm[tip].y > lm[mcp].y for tip, mcp in pairs)

def _is_open_palm(lm) -> bool:
    """True when all four fingertips are above their MCP knuckles."""
    pairs = [(8,5), (12,9), (16,13), (20,17)]
    return all(lm[tip].y < lm[mcp].y for tip, mcp in pairs)

def process(hands: dict) -> dict:
    """
    Args:
        hands: {'left': landmarks | None, 'right': landmarks | None}
    Returns:
        Normalized parameter dict ready for effect_map.apply().
    """
    state = {
        "left":  {"gesture": "none", "wrist_y": 0.5, "spread": 0.0},
        "right": {"gesture": "none", "wrist_y": 0.5, "pinch":  0.0},
    }

    lh = hands.get("left")
    if lh:
        lm = lh.landmark
        wy = _smooth("lh_wrist_y", _wrist_y(lm))
        sp = _smooth("lh_spread",  _spread(lm))
        state["left"]["wrist_y"] = wy
        state["left"]["spread"]  = sp
        if _is_open_palm(lm):
            state["left"]["gesture"] = "open_palm"
        elif _is_fist(lm):
            state["left"]["gesture"] = "fist"
        else:
            state["left"]["gesture"] = "neutral"

    rh = hands.get("right")
    if rh:
        lm = rh.landmark
        wy = _smooth("rh_wrist_y", _wrist_y(lm))
        pi = _smooth("rh_pinch",   _pinch(lm))
        state["right"]["wrist_y"] = wy
        state["right"]["pinch"]   = pi
        if _is_fist(lm):
            state["right"]["gesture"] = "fist"
        elif _is_open_palm(lm):
            state["right"]["gesture"] = "open_palm"
        else:
            state["right"]["gesture"] = "neutral"

    return state