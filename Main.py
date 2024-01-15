import mss
import numpy as np
import cv2
import keyboard
import time
import threading
import paho.mqtt.client as mqtt

# MQTT setup
broker_address = "insert IP"
port = 
topic = "cmnd/LuminaBulb/Color"

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

def on_publish(client, userdata, result):
    print("Data published")

def connect_mqtt():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_publish = on_publish
    client.connect(broker_address, port)
    return client

def capture_screen(capture_area, target_res):
    with mss.mss() as sct:
        # Grab the data + Access the captured image data and save to numpy array (RGBA format)
        img_np = np.array(sct.grab(capture_area))
          # Convert array data to BGR format for OpenCV
        img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGBA2BGR)
        img_bgr_resized = cv2.resize(img_bgr, target_res)
    return img_bgr_resized

def get_dominant_colour(image):
    # Reshape to 2D array and convert to 32-bit floating-point representation, each row represents a pixel (B, G, R)
    pixels = np.float32(image.reshape(-1, 3))
    n_colours = 4
    # Define criteria for Kmeans
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TermCriteria_MAX_ITER, 200, 0.2)
    # Group pixel colours into clusters
    _, labels, centers = cv2.kmeans(pixels, n_colours, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
    dominant_colour = centers[np.argmax(np.unique(labels, return_counts=True)[1])]
    # Convert to int representing RGB values
    return list(map(int, dominant_colour))

# send dominant colour to bulb via MQTT
def send_dominant_colour(client, capture_area, target_res, last_color, threshold):
    dom_colour = get_dominant_colour(capture_screen(capture_area, target_res))
    # Threshold check for colour change
    if not last_color or any(abs(c - lc) > threshold for c, lc in zip(dom_colour, last_color)):
        colour_message = f'{dom_colour[0]},{dom_colour[1]},{dom_colour[2]},0,0'
        client.publish(topic, colour_message)
        return dom_colour
    return last_color


def update_thread(client, target_res):
    last_color = None
    color_change_threshold = 15  # Adjust as needed
    while not exit_flag.is_set():
        if keyboard.is_pressed("q"):
            exit_flag.set()
            break
        last_color = send_dominant_colour(client, capture_area, target_res, last_color, color_change_threshold)
        time.sleep(0.1)

# Set the capture area and target resolution
capture_area = {"top": 0, "left": 0, "width": 2560, "height": 400}
target_res = (400, 400)

# MQTT client
mqtt_client = connect_mqtt()

# Create an exit flag for the thread
exit_flag = threading.Event()

# Start the update thread
update_thread = threading.Thread(target=update_thread, args=(mqtt_client, target_res,))
update_thread.start()

# Wait for the thread to finish
update_thread.join()
