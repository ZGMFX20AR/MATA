# Import necessary libraries
import cv2
import requests
import datetime
import time
import os
import RPi.GPIO as GPIO
import numpy as np
from picamera2 import Picamera2
from queue import Queue
from threading import Thread
from servo import Servo
import configparser

# Parse the configuration file
config = configparser.ConfigParser()
config.read('config.ini')

# Extract the Telegram API details
API_ENDPOINT_SEND_MESSAGE = config['telegram']['API_ENDPOINT_SEND_MESSAGE']
API_ENDPOINT_SEND_VIDEO = config['telegram']['API_ENDPOINT_SEND_VIDEO']
CHAT_ID = config['telegram']['CHAT_ID']

# Set GPIO mode to Broadcom SOC channel
GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.IN) 

pan_servo = Servo(2)
tilt_servo = Servo(3)
pan_servo.set_angle(0)
tilt_servo.set_angle(0)

picam2 = Picamera2()
picam2.preview_configuration.main.size = (1280, 720)
picam2.preview_configuration.main.format = "RGB888"
picam2.preview_configuration.align()
picam2.configure("preview")
picam2.start()

fourcc = cv2.VideoWriter_fourcc(*'XVID')
video_filename = f'motion_video_{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}.avi'
video_writer = cv2.VideoWriter(video_filename, fourcc, 30.0, (1280, 720))

fgbg = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=16, detectShadows=True)

motion_detected = False
frames_recorded = 0
MAX_FRAMES = 300

frame_queue = Queue()

def set_angle(angle, servo):
    if servo == 2:
        angle = np.clip(angle, 0, 180)  # Check the pan servo limits
        pan_servo.set_angle(angle)
    else:
        angle = np.clip(angle, 0, 180)  # Check the tilt servo limits
        tilt_servo.set_angle(angle)
    time.sleep(1)

def frame_processor():
    global motion_detected
    kernel = np.ones((5,5),np.uint8)

    while True:
        frame = frame_queue.get()

        if frame is None:
            break 

        fgmask = fgbg.apply(frame)

        fgmask = cv2.erode(fgmask, kernel, iterations = 1)
        fgmask = cv2.dilate(fgmask, kernel, iterations = 1)

        contours, _ = cv2.findContours(fgmask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            if cv2.contourArea(contour) > 1000:
                (x, y, w, h) = cv2.boundingRect(contour)
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

                center_x = x + w / 2
                center_y = y + h / 2

                pan_angle = (center_x / frame.shape[1]) * 180
                tilt_angle = (center_y / frame.shape[0]) * 180

                set_angle(pan_angle, 2)
                set_angle(tilt_angle, 3)

                if not motion_detected and GPIO.input(4) == 1:
                    motion_detected = True
                    data = {'chat_id': CHAT_ID, 'text': 'Motion detected.'}
                    try:
                        response = requests.post(API_ENDPOINT_SEND_MESSAGE, data=data)
                        print('Message sent, response:', response.json())
                    except requests.exceptions.RequestException as e:
                        print(f"Failed to send message: {e}")

        frame_queue.task_done()

frame_processor_thread = Thread(target=frame_processor)
frame_processor_thread.start()

while True:
    try:
        frame = picam2.capture_array()
        cv2.imshow("Camera", frame)
        frame_queue.put(frame)

        if motion_detected:
            video_writer.write(frame)
            frames_recorded += 1

            if frames_recorded >= MAX_FRAMES:
                video_writer.release()
                data = {'chat_id': CHAT_ID, 'caption': 'Motion video recorded at ' + str(datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))}
                with open(video_filename, 'rb') as f:
                    files = {'video': f}
                    try:
                        response = requests.post(API_ENDPOINT_SEND_VIDEO, data=data, files=files)
                        print('Video sent, response:', response.json())
                    except requests.exceptions.RequestException as e:
                        print(f"Failed to send video: {e}")

                video_filename = f'motion_video_{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}.avi'
                video_writer = cv2.VideoWriter(video_filename, fourcc, 30.0, (1280, 720))
                motion_detected = False
                frames_recorded = 0
                time.sleep(5)

        if cv2.waitKey(1) == ord('q'):
            break
    except Exception as e:
        print(f"Error: {e}")
        continue

cv2.destroyAllWindows()
video_writer.release()
picam2.stop()
GPIO.cleanup()
frame_queue.put(None)
frame_processor_thread.join()
