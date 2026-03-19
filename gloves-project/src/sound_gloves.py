import cv2
import mediapipe as mp
import voicemeeterlib

# setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7)

cap = cv2.VideoCapture(0)

# colors for each finger (BGR)
colors = [
    (0, 150, 255),   # thumb  - orange
    (200, 255, 0),   # index  - cyan
    (255, 0, 200),   # middle - purple
    (150, 0, 255),   # ring   - pink
    (255, 150, 0),   # pinky  - blue
]

fingertip_ids = [4, 8, 12, 16, 20]


def get_fingers(lm):
    fingers = []
    fingers.append(1 if lm[4].x < lm[3].x else 0)
    for tip in [8, 12, 16, 20]:
        fingers.append(1 if lm[tip].y < lm[tip - 2].y else 0)
    return fingers


def draw_hand(frame, lm, fingers):
    h, w = frame.shape[:2]

    # draw connections first
    for a, b in mp_hands.HAND_CONNECTIONS:
        x1, y1 = int(lm[a].x * w), int(lm[a].y * h)
        x2, y2 = int(lm[b].x * w), int(lm[b].y * h)
        cv2.line(frame, (x1, y1), (x2, y2), (180, 180, 180), 2)

    # draw all joints
    for i, point in enumerate(lm):
        x, y = int(point.x * w), int(point.y * h)
        if i in fingertip_ids:
            fi = fingertip_ids.index(i)
            size = 18 if fingers[fi] else 10
            cv2.circle(frame, (x, y), size, colors[fi], -1)
            if fingers[fi]:
                cv2.circle(frame, (x, y), size + 4, colors[fi], 2)
        else:
            cv2.circle(frame, (x, y), 6, (180, 180, 180), -1)


def update_voicemeeter(vm, fingers, wrist_y):
    # index = reverb on/off
    vm.strip[0].eq.on = bool(fingers[1])

    # middle = mute
    vm.strip[0].mute = bool(fingers[2])

    # ring = gain up, pinky = gain down
    if fingers[3]:
        vm.strip[0].gain = 6.0
    elif fingers[4]:
        vm.strip[0].gain = -6.0
    else:
        vm.strip[0].gain = 0.0

    # hand height controls master volume
    vol = round((1.0 - wrist_y) * 10 - 5, 1)
    vm.bus[0].gain = max(-10.0, min(6.0, vol))


effect_names = ["Thumb", "Reverb", "Mute", "Gain+", "Gain-"]

print("starting soundgloves...")

with voicemeeterlib.api('banana') as vm:
    while True:
        ret, frame = cap.read()
        frame = cv2.flip(frame, 1)
        results = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        if results.multi_hand_landmarks:
            for hand in results.multi_hand_landmarks:
                lm = hand.landmark
                fingers = get_fingers(lm)

                draw_hand(frame, lm, fingers)
                update_voicemeeter(vm, fingers, lm[0].y)

                for i, (name, val) in enumerate(zip(effect_names, fingers)):
                    color = colors[i] if val else (100, 100, 100)
                    cv2.putText(frame, f"{name}: {'on' if val else 'off'}",
                                (10, 30 + i * 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.65, color, 2)

        cv2.imshow("soundgloves", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()