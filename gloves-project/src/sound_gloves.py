# soundgloves.py
# Main loop for SoundGloves — Imogen Heap Mi.Mu glove simulator
# Requires: mediapipe, opencv-python, voicemeeterlib, python-rtmidi
#
# Run from the src/ folder:
#   python soundgloves.py

import cv2
import mediapipe as mp
import time
import sys

import gesture_engine
import effect_map
import midi_out
import overlay


# ─── startup ──────────────────────────────────────────────────────────────────

def _connect_all() -> bool:
    """Initialise MIDI and VoiceMeeter. Returns False if either fails."""
    ok_midi = midi_out.connect("loopMIDI")
    if not ok_midi:
        print("[soundgloves] WARNING: LoopMIDI port not found — "
              "MIDI effects (Valhalla, TAL-Vocoder) will be silent.\n"
              "  Open LoopMIDI and create a port, then restart.")

    try:
        effect_map.init_voicemeeter()
        ok_vm = True
    except Exception as e:
        print(f"[soundgloves] WARNING: VoiceMeeter connection failed: {e}\n"
              "  Make sure VoiceMeeter Banana is open, then restart.")
        ok_vm = False

    return ok_midi and ok_vm


def _parse_hands(results) -> dict:
    """
    Return {'left': landmarks | None, 'right': landmarks | None}
    Keyed by handedness label so index order never matters.
    """
    hands = {"left": None, "right": None}
    if not results.multi_hand_landmarks:
        return hands
    for lm, handed in zip(
        results.multi_hand_landmarks,
        results.multi_handedness,
    ):
        label = handed.classification[0].label.lower()  # "left" or "right"
        hands[label] = lm
    return hands


# ─── main loop ────────────────────────────────────────────────────────────────

def main():
    print("=" * 48)
    print("  SoundGloves  —  starting up")
    print("=" * 48)

    all_connected = _connect_all()
    if not all_connected:
        print("[soundgloves] Running in partial mode — some effects inactive.")

    # MediaPipe hands
    mp_hands   = mp.solutions.hands
    hands_model = mp_hands.Hands(
        max_num_hands=2,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.6,
        model_complexity=1,
    )

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[soundgloves] ERROR: Could not open webcam.")
        sys.exit(1)

    # Optional: set capture resolution for better performance
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT,  720)

    print("[soundgloves] Running — press Q to quit.\n")

    # Timing
    prev_time = time.time()
    fps        = 0.0

    # Last known state (used when no hands detected — holds display steady)
    gesture_state = {
        "left":  {"gesture": "none", "wrist_y": 0.5, "spread": 0.0},
        "right": {"gesture": "none", "wrist_y": 0.5, "pinch":  0.0},
    }
    applied = {}

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("[soundgloves] Frame read failed — camera disconnected?")
                break

            # Flip so it feels like a mirror
            frame = cv2.flip(frame, 1)
            h, w  = frame.shape[:2]

            # ── hand tracking ──────────────────────────────────────────────
            rgb     = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            rgb.flags.writeable = False          # perf: lock buffer for MP
            results = hands_model.process(rgb)
            rgb.flags.writeable = True

            hands = _parse_hands(results)

            # ── gesture → numbers ──────────────────────────────────────────
            gesture_state = gesture_engine.process(hands)

            # ── numbers → audio effects ────────────────────────────────────
            try:
                applied = effect_map.apply(gesture_state)
            except Exception as e:
                # Don't crash the visual loop if audio hiccups
                print(f"[effect_map] {e}")
                applied = {}

            # ── draw ───────────────────────────────────────────────────────
            # One draw_hand call per detected hand
            if results.multi_hand_landmarks:
                for lm, handed in zip(
                    results.multi_hand_landmarks,
                    results.multi_handedness,
                ):
                    side  = handed.classification[0].label          # "Left"/"Right"
                    label = gesture_state[side.lower()].get("gesture", side.lower())
                    frame = overlay.draw_hand(frame, lm, label)

            # HUD: parameter bars + mute indicator
            frame = overlay.draw_hud(frame, gesture_state, applied)

            # FPS counter (top-right, small)
            now       = time.time()
            fps       = 0.9 * fps + 0.1 * (1.0 / max(now - prev_time, 1e-6))
            prev_time = now
            cv2.putText(
                frame,
                f"{fps:.0f} fps",
                (w - 72, 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.42,
                (160, 160, 160),
                1,
                cv2.LINE_AA,
            )

            cv2.imshow("SoundGloves", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                print("[soundgloves] Q pressed — shutting down.")
                break

    finally:
        cap.release()
        cv2.destroyAllWindows()
        hands_model.close()
        effect_map.shutdown_voicemeeter()
        midi_out.close()
        print("[soundgloves] Clean shutdown.")


if __name__ == "__main__":
    main()