import cv2
import pyautogui
import mediapipe as mp
import time
from math import sqrt, pow
import speech_recognition as sr
import streamlit as st

# Initialize screen dimensions
screen_width, screen_height = pyautogui.size()

# Initialize MediaPipe components
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

# Global variables for tracking states
initial = None
initialtime = time.time()
switchappmenu = None

def mediapipe_detection(image, model):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image.flags.writeable = False
    results = model.process(image)
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    return image, results

def mousecondition(landmarks, h):
    ringfingertip = landmarks[16].y * h
    pinkyfingertip = landmarks[20].y * h
    ringfingerbase = landmarks[13].y * h
    pinkyfingerbase = landmarks[17].y * h
    indexfingertip = landmarks[8].y * h
    indexfingermiddle = landmarks[6].y * h

    return ringfingerbase < ringfingertip and pinkyfingerbase < pinkyfingertip and indexfingermiddle > indexfingertip

def switchapps(landmarks, h):
    middlefingertip = landmarks[12].y * h
    ringfingertip = landmarks[16].y * h
    pinkyfingertip = landmarks[20].y * h
    middlefingerbase = landmarks[9].y * h
    ringfingerbase = landmarks[13].y * h
    pinkyfingerbase = landmarks[17].y * h
    indexfingertip = landmarks[8].y * h
    indexfingerbase = landmarks[5].y * h

    return middlefingerbase < middlefingertip and ringfingerbase < ringfingertip and pinkyfingerbase > pinkyfingertip and indexfingerbase > indexfingertip

def volume_up_down(landmarks, h):
    thumb_tip = landmarks[4].y * h
    index_tip = landmarks[8].y * h
    middle_tip = landmarks[12].y * h

    if thumb_tip < index_tip < middle_tip:
        return 'volume_up'
    elif thumb_tip > index_tip > middle_tip:
        return 'volume_down'
    else:
        return None

def screenshot_condition(landmarks, h):
    thumb_tip = landmarks[4].y * h
    index_tip = landmarks[8].y * h
    middle_tip = landmarks[12].y * h
    ring_tip = landmarks[16].y * h
    pinky_tip = landmarks[20].y * h

    return thumb_tip < index_tip and thumb_tip < middle_tip and thumb_tip < ring_tip and thumb_tip < pinky_tip

def cut_condition(landmarks, h):
    thumb_tip = landmarks[4].y * h
    index_tip = landmarks[8].y * h
    middle_tip = landmarks[12].y * h
    ring_tip = landmarks[16].y * h

    return thumb_tip > index_tip > middle_tip > ring_tip

def swipe_up_condition(landmarks, h):
    index_tip = landmarks[8].y * h
    index_base = landmarks[5].y * h

    return index_tip < index_base

def swipe_down_condition(landmarks, h):
    index_tip = landmarks[8].y * h
    index_base = landmarks[5].y * h

    return index_tip > index_base

def draw_styled_landmarks(image, results):
    global initial, initialtime, switchappmenu
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            l = hand_landmarks.landmark
            h, w, _ = image.shape

            thumb = (int(l[4].x * w), int(l[4].y * h))
            indexfinger = (int(l[5].x * w), int(l[5].y * h))
            pinkyfinger = (int(l[17].x * w), int(l[17].y * h))
            middlefingertip = l[12].y * h
            middlefingerbase = l[9].y * h

            if mousecondition(l, h):
                if switchappmenu:
                    switchappmenu = False
                if middlefingerbase > middlefingertip:
                    pyautogui.rightClick()
                    time.sleep(0.2)
                else:
                    if thumb > indexfinger:
                        pass
                    else:
                        if int(time.time() - initialtime) < 1:
                            pyautogui.doubleClick()
                            initialtime = time.time()
                        else:
                            pyautogui.click()
                            initialtime = time.time()
                pyautogui.moveTo(screen_width * l[8].x, screen_height * l[8].y)

            elif switchapps(l, h):
                if switchappmenu:
                    if initial is None:
                        initial = (int(l[8].x * w), int(l[8].y * h))
                    distance = sqrt(pow(l[8].x * w - initial[0], 2) + pow(l[8].y * h - initial[1], 2))
                    if abs(initial[1] - int(l[8].y * h)) < h / 8 and distance >= w / 8:
                        if initial[0] > int(l[8].x * w):
                            pyautogui.press('left')
                            initial = (int(l[8].x * w), int(l[8].y * h))
                        elif initial[0] < int(l[8].x * w):
                            pyautogui.press('right')
                            initial = (int(l[8].x * w), int(l[8].y * h))
                    elif not (thumb > indexfinger):
                        pyautogui.keyUp('alt')
                        switchappmenu = False
                        initial = (int(l[8].x * w), int(l[8].y * h))
                        time.sleep(1)
                else:
                    pyautogui.keyDown('alt')
                    pyautogui.press('tab')
                    switchappmenu = True

            else:
                switchappmenu = False

                vol_result = volume_up_down(l, h)
                if vol_result == 'volume_up':
                    pyautogui.press('volumeup')
                    time.sleep(0.2)
                elif vol_result == 'volume_down':
                    pyautogui.press('volumedown')
                    time.sleep(0.2)
                elif screenshot_condition(l, h):
                    pyautogui.screenshot('screenshot.png')
                    time.sleep(1)
                elif cut_condition(l, h):
                    pyautogui.hotkey('ctrl', 'x')
                    time.sleep(1)
                elif swipe_up_condition(l, h):
                    pyautogui.scroll(100)
                    time.sleep(0.2)
                elif swipe_down_condition(l, h):
                    pyautogui.scroll(-100)
                    time.sleep(0.2)

                if initial is None:
                    initial = (int(l[8].x * w), int(l[8].y * h))
                distance = sqrt(pow(l[8].x * w - initial[0], 2) + pow(l[8].y * h - initial[1], 2))
                if distance >= w / 2 and abs(initial[1] - int(l[8].y * h)) < h / 8:
                    if initial[0] > int(l[8].x * w):
                        pass
                    if initial[0] < int(l[8].x * w):
                        pass
                elif distance >= h / 4 and abs(initial[0] - int(l[8].x * w)) < w / 8:
                    if initial[1] > int(l[8].y * h):
                        pyautogui.hotkey('win', 'shift', 'm')
                    if initial[1] < int(l[8].y * h):
                        pyautogui.hotkey('win', 'm')
                cv2.line(image, initial, (int(l[8].x * w), int(l[8].y * h)), (255, 0, 245), 10)
                initial = (int(l[8].x * w), int(l[8].y * h))

            mp_drawing.draw_landmarks(
                image,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS,
                mp_drawing_styles.get_default_hand_landmarks_style(),
                mp_drawing_styles.get_default_hand_connections_style())

# Initialize MediaPipe hands detection
hands = mp_hands.Hands(
    model_complexity=1,
    min_detection_confidence=0.95,
    min_tracking_confidence=0.8)

def voice_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("Listening for commands...")
        audio = recognizer.listen(source)
        try:
            command = recognizer.recognize_google(audio).lower()
            st.write(f"Command received: {command}")
            if "open google chrome" in command:
                pyautogui.hotkey('win', 'r')
                pyautogui.typewrite('chrome')
                pyautogui.press('enter')
            elif "open ms word" in command:
                pyautogui.hotkey('win', 'r')
                pyautogui.typewrite('winword')
                pyautogui.press('enter')
            elif "open excel" in command:
                pyautogui.hotkey('win', 'r')
                pyautogui.typewrite('excel')
                pyautogui.press('enter')
            elif "open vscode" in command:
                pyautogui.hotkey('win', 'r')
                pyautogui.typewrite('code')
                pyautogui.press('enter')
            elif "shut down" in command:
                pyautogui.hotkey('win', 'r')
                pyautogui.typewrite('shutdown /s /t 0')
                pyautogui.press('enter')
            elif "sleep" in command:
                pyautogui.hotkey('win', 'x')
                pyautogui.press('u')
                pyautogui.press('s')
        except sr.UnknownValueError:
            st.write("Sorry, I did not understand the command.")
        except sr.RequestError:
            st.write("Could not request results; check your network connection.")

# Streamlit setup
st.title("Hand Gesture and Voice Command Control")
st.write("Press 'Start Webcam' to begin hand tracking and gesture control.")
st.write("Say 'Open Google Chrome', 'Open MS Word', 'Open Excel', 'Open VS Code', 'Shut down', or 'Sleep' for voice commands.")

if st.button('Start Webcam'):
    webcam = cv2.VideoCapture(0)
    while True:
        _, frame = webcam.read()
        frame = cv2.flip(frame, 1)  # Flip the frame horizontally
        frame, results = mediapipe_detection(frame, hands)
        draw_styled_landmarks(frame, results)
        cv2.imshow("Hand Tracking", frame)
        if cv2.waitKey(27) & 0xFF == ord('q'):
            break
    webcam.release()
    cv2.destroyAllWindows()

if st.button('Voice Command'):
    voice_command()
