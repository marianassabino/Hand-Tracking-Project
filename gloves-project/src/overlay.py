# overlay.py
import cv2
import numpy as np
import mediapipe as mp

# --- Visual constants ---
LAVENDER       = (220, 180, 255)   # BGR for OpenCV
LAVENDER_DIM   = (160, 120, 200)   # dimmer version for fan lines
WHITE          = (255, 255, 255)
BOX_ALPHA      = 0.15              # bounding box fill transparency
DOT_RADIUS     = 6                 # landmark dot size
DOT_THICKNESS  = -1                # filled circle
LINE_THICKNESS = 1
FONT           = cv2.FONT_HERSHEY_SIMPLEX

# MediaPipe connections (subset — just the clean ones)
mp_hands = mp.solutions.hands
CONNECTIONS = mp_hands.HAND_CONNECTIONS

# Fan lines: from wrist (0) to each fingertip
FAN_TIPS = [4, 8, 12, 16, 20]  # thumb → pinky tips


def _draw_smooth_dot(frame, cx, cy, color, radius=DOT_RADIUS):
    """Antialiased filled circle with a soft outer ring."""
    cv2.circle(frame, (cx, cy), radius + 2, (*color, 0), 1,
               lineType=cv2.LINE_AA)
    cv2.circle(frame, (cx, cy), radius, color, DOT_THICKNESS,
               lineType=cv2.LINE_AA)


def _draw_bounding_box(frame, lm_list, h, w, label: str):
    """Translucent rounded bounding box + gesture label, like the reference."""
    xs = [int(lm.x * w) for lm in lm_list]
    ys = [int(lm.y * h) for lm in lm_list]
    pad = 24
    x1, y1 = max(0, min(xs) - pad), max(0, min(ys) - pad)
    x2, y2 = min(w, max(xs) + pad), min(h, max(ys) + pad)

    # Translucent fill
    overlay = frame.copy()
    cv2.rectangle(overlay, (x1, y1), (x2, y2), LAVENDER, -1)
    cv2.addWeighted(overlay, BOX_ALPHA, frame, 1 - BOX_ALPHA, 0, frame)

    # Border
    cv2.rectangle(frame, (x1, y1), (x2, y2), LAVENDER, 1,
                  lineType=cv2.LINE_AA)

    # Label at top of box
    label_y = max(y1 - 8, 16)
    cv2.putText(frame, label, (x1, label_y),
                FONT, 0.55, LAVENDER, 1, cv2.LINE_AA)


def _draw_fan_lines(frame, lm_list, h, w):
    """Thin lines from wrist to each fingertip — the fan effect."""
    wrist = lm_list[0]
    wx, wy = int(wrist.x * w), int(wrist.y * h)
    for tip_id in FAN_TIPS:
        tip = lm_list[tip_id]
        tx, ty = int(tip.x * w), int(tip.y * h)
        cv2.line(frame, (wx, wy), (tx, ty), LAVENDER_DIM, LINE_THICKNESS,
                 lineType=cv2.LINE_AA)


def _draw_skeleton(frame, lm_list, h, w):
    """Draw the hand skeleton connections in lavender."""
    for connection in CONNECTIONS:
        a, b = connection
        ax = int(lm_list[a].x * w)
        ay = int(lm_list[a].y * h)
        bx = int(lm_list[b].x * w)
        by = int(lm_list[b].y * h)
        cv2.line(frame, (ax, ay), (bx, by), LAVENDER_DIM, LINE_THICKNESS,
                 lineType=cv2.LINE_AA)


def _draw_landmarks(frame, lm_list, h, w):
    """Draw all 21 landmark dots."""
    for lm in lm_list:
        cx = int(lm.x * w)
        cy = int(lm.y * h)
        _draw_smooth_dot(frame, cx, cy, LAVENDER)


def draw_hand(frame, hand_landmarks, label: str):
    """
    Draw one hand: bounding box, fan lines, skeleton, dots.
    Call once per detected hand per frame.
    """
    h, w = frame.shape[:2]
    lm_list = hand_landmarks.landmark

    _draw_bounding_box(frame, lm_list, h, w, label)
    _draw_fan_lines(frame, lm_list, h, w)
    _draw_skeleton(frame, lm_list, h, w)
    _draw_landmarks(frame, lm_list, h, w)

    return frame


def draw_hud(frame, gesture_state: dict, applied: dict):
    """
    Draw the full HUD: hands + parameter bars at the bottom.
    Call this from soundgloves.py with the results of gesture_engine + effect_map.
    """
    h, w = frame.shape[:2]

    # Parameter bars along the bottom
    params = [
        ("reverb",  applied.get("reverb_mix", 0.0),  LAVENDER),
        ("vocoder", applied.get("carrier",    0.0),  (255, 200, 150)),
        ("pitch",   (applied.get("pitch_db", 0.0) + 6) / 12, (200, 255, 200)),
    ]
    bar_h   = 6
    bar_y   = h - 20
    bar_w   = w // len(params)

    for i, (name, val, color) in enumerate(params):
        bx = i * bar_w
        fill = int(max(0.0, min(1.0, val)) * bar_w)
        # Track
        cv2.rectangle(frame, (bx, bar_y), (bx + bar_w, bar_y + bar_h),
                      (40, 40, 40), -1)
        # Fill
        cv2.rectangle(frame, (bx, bar_y), (bx + fill, bar_y + bar_h),
                      color, -1, lineType=cv2.LINE_AA)
        # Label
        cv2.putText(frame, name, (bx + 4, bar_y - 6),
                    FONT, 0.38, color, 1, cv2.LINE_AA)

    # Mute indicator
    if applied.get("mute"):
        cv2.putText(frame, "MUTED", (w // 2 - 30, 30),
                    FONT, 0.7, (80, 80, 255), 2, cv2.LINE_AA)

    return frame