# soundgloves.py
# Main loop for SoundGloves — Imogen Heap Mi.Mu glove simulator
# Requires: mediapipe, opencv-python, python-rtmidi
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


# ── startup ───────────────────────────────────────────────────────────────────

def _connect_all() -> bool:
    ok_midi = midi_out.connect("loopMIDI")
    if not ok_midi:
        print("[soundgloves] WARNING: LoopMIDI port not found.\n"
              "  Open LoopMIDI and make sure a port exists, then restart.")
        return False
    effect_map.init()
    return True


def _parse_hands(results) -> dict:
    hands = {"left": None, "right": None}
    if not results.multi_hand_landmarks:
        return hands
    for lm, handed in zip(
        results.multi_hand_landmarks,
        results.multi_handedness,
    ):
        label = handed.classification[0].label.lower()
        hands[label] = lm
    return hands


# ── main loop ─────────────────────────────────────────────────────────────────

def main():
    print("=" * 48)
    print("  SoundGloves  —  starting up")
    print("=" * 48)

    _connect_all()

    mp_hands    = mp.solutions.hands
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

    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT,  720)

    print("[soundgloves] Running — press Q to quit.\n")

    prev_time = time.time()
    fps       = 0.0

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

            frame = cv2.flip(frame, 1)
            h, w  = frame.shape[:2]

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            rgb.flags.writeable = False
            results = hands_model.process(rgb)
            rgb.flags.writeable = True

            hands = _parse_hands(results)
            gesture_state = gesture_engine.process(hands)

            try:
                applied = effect_map.apply(gesture_state)
            except Exception as e:
                print(f"[effect_map] {e}")
                applied = {}

            if results.multi_hand_landmarks:
                for lm, handed in zip(
                    results.multi_hand_landmarks,
                    results.multi_handedness,
                ):
                    side  = handed.classification[0].label
                    label = gesture_state[side.lower()].get("gesture", side.lower())
                    frame = overlay.draw_hand(frame, lm, label)

            frame = overlay.draw_hud(frame, gesture_state, applied)

            now       = time.time()
            fps       = 0.9 * fps + 0.1 * (1.0 / max(now - prev_time, 1e-6))
            prev_time = now
            cv2.putText(
                frame, f"{fps:.0f} fps",
                (w - 72, 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.42, (160, 160, 160), 1, cv2.LINE_AA,
            )

            cv2.imshow("SoundGloves", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                print("[soundgloves] Q pressed — shutting down.")
                break

    finally:
        cap.release()
        cv2.destroyAllWindows()
        hands_model.close()
        effect_map.shutdown()
        midi_out.close()
        print("[soundgloves] Clean shutdown.")


if __name__ == "__main__":
    main()