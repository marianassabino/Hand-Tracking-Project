import cv2
import mediapipe as mp
import numpy as np
import sounddevice as sd
import queue
from scipy.signal import resample

# ─── Audio Settings ───────────────────────────────────────
RATE = 48000
CHUNK = 1024
q_in = queue.Queue()

# ─── Effects State ────────────────────────────────────────
effects = {
    "echo":       False,
    "reverb":     False,
    "pitch_up":   False,
    "pitch_down": False,
}
volume = 1.0
echo_buffer = np.zeros((int(RATE * 0.3), 2), dtype=np.float32)
echo_pos = 0

# ─── Audio Processing ─────────────────────────────────────
def apply_effects(data):
    global echo_buffer, echo_pos, volume
    samples = data.astype(np.float32)
    samples *= volume

    if effects["echo"]:
        delay = int(RATE * 0.3)
        for i in range(len(samples)):
            echo_val = echo_buffer[echo_pos].copy()
            echo_buffer[echo_pos] = samples[i]
            samples[i] += 0.5 * echo_val
            echo_pos = (echo_pos + 1) % delay

    if effects["reverb"]:
        reverb = np.zeros_like(samples)
        for d, g in [(int(RATE*0.03), 0.6), (int(RATE*0.05), 0.4), (int(RATE*0.08), 0.3)]:
            if len(samples) > d:
                reverb[d:] += g * samples[:-d]
        samples = samples + reverb

    if effects["pitch_up"]:
        factor = 0.75
        indices = np.round(np.arange(0, len(samples), factor)).astype(int)
        indices = indices[indices < len(samples)]
        stretched = samples[indices]
        samples = stretched[:CHUNK] if len(stretched) >= CHUNK else np.pad(stretched, ((0, CHUNK - len(stretched)), (0, 0)))

    if effects["pitch_down"]:
        factor = 1.5
        old_len = len(samples)
        new_len = int(old_len / factor)
        stretched = np.array([np.interp(np.linspace(0, old_len-1, new_len), 
                              np.arange(old_len), samples[:, ch]) 
                              for ch in range(samples.shape[1])]).T
        samples = np.pad(stretched, ((0, CHUNK - len(stretched)), (0, 0))) if len(stretched) < CHUNK else stretched[:CHUNK]

    return np.clip(samples, -32767, 32767).astype(np.int16)

# ─── Audio Callbacks ──────────────────────────────────────
def input_callback(indata, frames, time, status):
    if status:
        print(status)
    q_in.put(indata.copy())

def output_callback(outdata, frames, time, status):
    if status:
        print(status)
    try:
        data = q_in.get_nowait()
        outdata[:] = apply_effects(data)
    except queue.Empty:
        outdata[:] = 0

# ─── Hand Tracking ────────────────────────────────────────
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_draw = mp.solutions.drawing_utils

def fingers_up(landmarks):
    fingers = []
    if landmarks[4].x < landmarks[3].x:
        fingers.append(1)
    else:
        fingers.append(0)
    for tip_id in [8, 12, 16, 20]:
        if landmarks[tip_id].y < landmarks[tip_id - 2].y:
            fingers.append(1)
        else:
            fingers.append(0)
    return fingers

cap = cv2.VideoCapture(0)

print("🎤 Starting Voice Gloves...")

with sd.InputStream(samplerate=RATE, blocksize=CHUNK,
                    device=17, channels=2,
                    dtype='int16', callback=input_callback):
    with sd.OutputStream(samplerate=RATE, blocksize=CHUNK,
                         device=14, channels=2,
                         dtype='int16', callback=output_callback):
        print("✅ Audio active! Show your hand!")

        while True:
            ret, frame = cap.read()
            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb)

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                    lm = hand_landmarks.landmark
                    fingers = fingers_up(lm)

                    effects["echo"]       = bool(fingers[1])
                    effects["reverb"]     = bool(fingers[2])
                    effects["pitch_up"]   = bool(fingers[3])
                    effects["pitch_down"] = bool(fingers[4])

                    wrist_y = lm[0].y
                    volume = max(0.1, min(2.0, 1.5 - wrist_y))

                    labels = ["Echo", "Reverb", "Pitch Up", "Pitch Down"]
                    vals = [fingers[1], fingers[2], fingers[3], fingers[4]]

                    for i, (name, val) in enumerate(zip(labels, vals)):
                        color = (0, 255, 0) if val else (0, 0, 255)
                        cv2.putText(frame, f"{name}: {'ON' if val else 'OFF'}",
                                   (10, 30 + i * 30),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

                    cv2.putText(frame, f"Volume: {round(volume, 2)}",
                               (10, 160), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

            cv2.imshow("Voice Gloves 🎤", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

cap.release()
cv2.destroyAllWindows()