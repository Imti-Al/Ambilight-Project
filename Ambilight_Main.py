import mss
import numpy as np
import cv2
import tkinter as tk
import keyboard

def capture_screen(capture_area):
    with mss.mss() as sct:
        # Set capture area (x, y, width, height)
        #capture_area = {"top": 0, "left": 0, "width": 1920, "height": 1080}

        # Grab the data + Access the captured image data and save to numpy array (RGBA format)
        img_np = np.array(sct.grab(capture_area))

        # Convert array data to BGR format for OpenCV
        img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGBA2BGR)

    return img_bgr

def get_dominant_colour(image):
    # Reshape to 2D array and convert to 32-bit floating-point representation, each row represents a pixel (B, G, R)
    pixels = np.float32(image.reshape(-1, 3))

    # Number of dominant colours to be extracted
    n_colours = 8

    # Define criteria for Kmeans
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TermCriteria_MAX_ITER, 200, 0.2)

    # Group pixel colours into clusters
    _, labels, centers = cv2.kmeans(pixels, n_colours, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)

    # Identify dominant colours
    dominant_colour = centers[np.argmax(np.unique(labels, return_counts=True)[1])]

    # Convert to int representing RGB values
    return list(map(int, dominant_colour))


def update_colour(canvas, capture_area):
    dom_colour = get_dominant_colour(capture_screen(capture_area))

    # Convert dom colour to hex 
    colour_hex = "#{:02x}{:02x}{:02x}".format(*dom_colour)
    # create canvas and fill with hex dom colour
    canvas.create_rectangle(0, 0, 200, 200, fill=colour_hex, outline="")
    canvas.update()

capture_area = {"top": 0, "left": 0, "width": 2560, "height": 400}

root = tk.Tk()
root.title("Dom Colour Test")

canvas = tk.Canvas(root, width=200, height=200)
canvas.pack()

# loop to continuously update colour
while True:
    update_colour(canvas, capture_area)
    time.sleep(0.1) # throttle update rate

    # Exit program is 'q' is pressed
    if keyboard.is_pressed("q"):
        break

# Close the Tkinter window when the program exits
root.destroy()