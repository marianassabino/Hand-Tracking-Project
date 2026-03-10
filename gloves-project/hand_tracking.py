import cv2
import mediapipe as mp
import winsound
import threading

mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_draw = mp.solutions.drawing_utils

FINGER_NAMES = ["Thumb", "Index", "Middle", "Ring", "Pinky"]

prev_fingers = [0, 0, 0, 0, 0]

def play_sound(filename):
    threading.Thread(target=winsound.PlaySound,
                    args=(filename, winsound.SND_FILENAME),
                    daemon=True).start()

cap = cv2.VideoCapture(0)

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

            for i, (name, status) in enumerate(zip(FINGER_NAMES, fingers)):
                # Play sound only when finger goes UP
                if status == 1 and prev_fingers[i] == 0:
                    play_sound(f"sounds/{name.lower()}.wav")

                color = (0, 255, 0) if status else (0, 0, 255)
                cv2.putText(frame, f"{name}: {'UP' if status else 'DOWN'}",
                           (10, 30 + i * 30), cv2.FONT_HERSHEY_SIMPLEX,
                           0.7, color, 2)

            prev_fingers = fingers

    cv2.imshow("Hand Tracking", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()