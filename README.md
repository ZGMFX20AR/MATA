
Motion activated pan-tilt camera
![MATA (1)](https://github.com/ZGMFX20AR/MATA/assets/55775578/3451b27d-c313-40b3-932b-ff4b3bfab8ad)
![Animation](https://github.com/ZGMFX20AR/MATA/assets/55775578/99e8ee7a-7cbb-49ea-a39c-e1d0c85167f3)
# Motion Detection and Tracking with Raspberry Pi

This Python script captures video feed from a Raspberry Pi Camera, detects motion using background subtraction, and tracks the motion using servo motors. Detected motion is communicated via Telegram messages, and video clips are sent when significant motion events occur.

## Prerequisites

- Raspberry Pi with Raspbian OS
- Python 3.x
- OpenCV library (`cv2`)
- `requests` library
- `RPi.GPIO` library
- `picamera2` library

## Setup and Configuration

1. Install required libraries:
   ```bash
   pip install opencv-python RPi.GPIO picamera[array] requests

Sure, here's a basic README.md file for the provided code. Remember to update it with any additional information or context that you think would be helpful for someone who's going through your code:

markdown
Copy code
# Motion Detection and Tracking with Raspberry Pi

This Python script captures video feed from a Raspberry Pi Camera, detects motion using background subtraction, and tracks the motion using servo motors. Detected motion is communicated via Telegram messages, and video clips are sent when significant motion events occur.

## Prerequisites

- Raspberry Pi with Raspbian OS
- Python 3.x
- OpenCV library (`cv2`)
- `requests` library
- `RPi.GPIO` library
- `picamera2` library

## Setup and Configuration

1. Install required libraries:
   ```bash
   pip install opencv-python RPi.GPIO picamera[array] requests
Clone or download this repository:

Create a config.ini file and populate it with your Telegram API details and other settings.

Connect the required hardware, including Raspberry Pi Camera and servo motors.

Run the script:

python motion_detection.py


Functionality
The script captures video frames using the Raspberry Pi Camera.
Motion detection is performed using background subtraction (cv2.createBackgroundSubtractorMOG2).
Detected motion triggers the servo motors to track the motion.
Telegram messages are sent when motion is detected.
Video clips are recorded and sent via Telegram when significant motion events occur.
Press 'q' to exit the script.


Contributing
Contributions are welcome! Please open an issue or submit a pull request if you have any improvements, suggestions, or bug fixes.
