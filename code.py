import cv2
import mediapipe as mp
import numpy as np
from time import sleep
import math
from pynput.keyboard import Controller

mpHands = mp.solutions.hands
hands = mpHands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5, min_tracking_confidence=0.5)
mpdraw = mp.solutions.drawing_utils

keyboard = Controller()

cap = cv2.VideoCapture(0)
cap.set(2, 150)

text = ""
redo_stack = []
tx = ""

class Button():
    def __init__(self, pos, text, size=[70, 70]):
        self.pos = pos
        self.size = size
        self.text = text

# Add numbers row to the keyboard
keys = [["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "CL"],
        ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P", "SP"],
        ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";", "APR"],
        ["Z", "X", "C", "V", "B", "N", "M", ",", ".", "/", "REDO"]]

keys1 = [["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "CL"],
         ["q", "w", "e", "r", "t", "y", "u", "i", "o", "p", "SP"],
         ["a", "s", "d", "f", "g", "h", "j", "k", "l", ";", "APR"],
         ["z", "x", "c", "v", "b", "n", "m", ",", ".", "/", "REDO"]]

# Function to draw all buttons
def drawAll(img, buttonList):
    for button in buttonList:
        x, y = button.pos
        w, h = button.size
        cv2.rectangle(img, button.pos, (x + w, y + h), (96, 96, 96), cv2.FILLED)
        cv2.putText(img, button.text, (x + 10, y + 40), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)
    return img

# Create button lists
buttonList = []
buttonList1 = []

for i in range(len(keys)):
    for j, key in enumerate(keys[i]):
        buttonList.append(Button([80 * j + 10, 80 * i + 10], key))
for i in range(len(keys1)):
    for j, key in enumerate(keys1[i]):
        buttonList1.append(Button([80 * j + 10, 80 * i + 10], key))

# Initialize variables
app = 0
delay = 0

def calculate_distance(x1, y1, x2, y2):
    distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    return distance

# Coefficient calculation for distance scaling
x = [300, 245, 200, 170, 145, 130, 112, 103, 93, 87, 80, 75, 70, 67, 62, 59, 57]
y = [20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100]
coff = np.polyfit(x, y, 2)

# Main loop
while True:
    success, frame = cap.read()
    frame = cv2.resize(frame, (1000, 580))
    frame = cv2.flip(frame, 1)
    img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(img)
    lanmark = []

    if app == 0:
        frame = drawAll(frame, buttonList)
        list = buttonList
        r = "up"
    else:
        frame = drawAll(frame, buttonList1)
        list = buttonList1
        r = "down"

    if results.multi_hand_landmarks:
        for hn in results.multi_hand_landmarks:
            for id, lm in enumerate(hn.landmark):
                hl, wl, cl = frame.shape
                cx, cy = int(lm.x * wl), int(lm.y * hl)
                lanmark.append([id, cx, cy])

    if lanmark:
        try:
            x5, y5 = lanmark[5][1], lanmark[5][2]
            x17, y17 = lanmark[17][1], lanmark[17][2]
            dis = calculate_distance(x5, y5, x17, y17)
            A, B, C = coff
            distanceCM = A * dis ** 2 + B * dis + C

            if 20 < distanceCM < 50:
                x, y = lanmark[8][1], lanmark[8][2]
                x2, y2 = lanmark[6][1], lanmark[6][2]
                x3, y3 = lanmark[12][1], lanmark[12][2]
                cv2.circle(frame, (x, y), 20, (255, 0, 255), cv2.FILLED)
                cv2.circle(frame, (x3, y3), 20, (255, 0, 255), cv2.FILLED)

                if y2 > y:
                    for button in list:
                        xb, yb = button.pos
                        wb, hb = button.size
                        if xb < x < xb + wb and yb < y < yb + hb:
                            cv2.rectangle(frame, (xb - 5, yb - 5), (xb + wb + 5, yb + hb + 5), (160, 160, 160), cv2.FILLED)
                            cv2.putText(frame, button.text, (xb + 20, yb + 65), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)
                            dis = calculate_distance(x, y, x3, y3)
                            if dis < 50 and delay == 0:
                                k = button.text
                                if k == "SP":
                                    text += ' '
                                    keyboard.press(' ')
                                elif k == "CL":
                                    if text:
                                        redo_stack.append(text[-1])
                                        text = text[:-1]
                                        keyboard.press('')
                                elif k == "APR" and r == "up":
                                    app = 1
                                elif k == "APR" and r == "down":
                                    app = 0
                                elif k == "REDO":
                                    if redo_stack:
                                        char = redo_stack.pop()
                                        text += char
                                        keyboard.press(char)
                                else:
                                    text += k
                                    keyboard.press(k)
                                delay = 1
        except:
            pass

    if delay != 0:
        delay += 1
        if delay > 10:
            delay = 0

    cv2.rectangle(frame, (20, 450), (850, 600), (255, 255, 255), cv2.FILLED)
    cv2.putText(frame, text, (30, 500), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 0), 3)
    cv2.imshow('Virtual Keyboard', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
