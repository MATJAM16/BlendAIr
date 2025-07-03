"""Minimal gesture detection using MediaPipe Hands.
Runs in a separate thread when user toggles gesture mode.
Actual mapping kept simple for demo purposes.
"""

import cv2  # type: ignore
import threading
from collections import deque

try:
    from mediapipe import solutions as mp_solutions  # type: ignore
except ImportError:
    mp_solutions = None

from .utils import enqueue_job

def _detect_gestures(threshold: float):
    if mp_solutions is None:
        return
    hands = mp_solutions.hands.Hands(max_num_hands=1)
    cap = cv2.VideoCapture(0)
    recent = deque(maxlen=5)
    from . import history
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        res = hands.process(rgb)
        if res.multi_hand_landmarks:
            recent.append("open")
        else:
            recent.append("none")
        if recent.count("open") > 3:
            enqueue_job({"func": print, "args": ("Gesture detected: open palm",)})
            try:
                history.log_gesture(user_id='local', project_id='demo', gesture='open_palm')
            except Exception:
                pass
            recent.clear()
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()

is_gesture_active = False
_gesture_thread = None

def toggle_gesture_listener(threshold: float = 0.7):
    global is_gesture_active, _gesture_thread
    if not is_gesture_active:
        _gesture_thread = threading.Thread(target=_detect_gestures, args=(threshold,), daemon=True)
        _gesture_thread.start()
        is_gesture_active = True
    else:
        is_gesture_active = False

def start_gesture_listener(threshold: float = 0.7):
    toggle_gesture_listener(threshold)

def register():
    pass

def unregister():
    pass
