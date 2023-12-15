import mss
import numpy as np
import cv2
import tkinter as tk
import keyboard
import time
import threading

def capture_screen(capture_area, target_res):
    with mss.mss() as sct:
        # Set capture area (x, y, width, height)
        #capture_area = {"top": 0, "left": 0, "width": 1920, "height": 1080}

        # Grab the data + Access the captured image data and save to numpy array (RGBA format)
        img_np = np.array(sct.grab(capture_area))

        # Convert array data to BGR format for OpenCV
        img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGBA2BGR)
        # Resize image
        img_bgr_resized = cv2.resize(img_bgr, target_res)

    return img_bgr_resized

def get_dominant_colour(image):
    # Reshape to 2D array and convert to 32-bit floating-point representation, each row represents a pixel (B, G, R)
    pixels = np.float32(image.reshape(-1, 3))

    # Number of dominant colours to be extracted
    n_colours = 4

    # Define criteria for Kmeans
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TermCriteria_MAX_ITER, 200, 0.2)

    # Group pixel colours into clusters
    _, labels, centers = cv2.kmeans(pixels, n_colours, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)

    # Identify dominant colours
    dominant_colour = centers[np.argmax(np.unique(labels, return_counts=True)[1])]

    # Convert to int representing RGB values
    return list(map(int, dominant_colour))


def update_colour(canvas, capture_area, target_res):
    dom_colour = get_dominant_colour(capture_screen(capture_area, target_res))

    # Convert dom colour to hex 
    colour_hex = "#{:02x}{:02x}{:02x}".format(*dom_colour)
    # create canvas and fill with hex dom colour
    canvas.create_rectangle(0, 0, 400, 400, fill=colour_hex, outline="")
    canvas.update()

def update_thread(target_res):
    while not exit_flag.is_set():
        if keyboard.is_pressed("q"):
            exit_flag.set()
            root.destroy() # Close Tkinter
            break
        update_colour(canvas, capture_area, target_res)
        time.sleep(0.2)

# Set the capture are and target resolution
capture_area = {"top": 0, "left": 0, "width": 2560, "height": 400}
target_res = (400, 400)

# Create Tkinter window and canvas
root = tk.Tk()
root.title("Dom Colour Test")
canvas = tk.Canvas(root, width=200, height=200)
canvas.pack()

# Create an exit flag for the thread
exit_flag = threading.Event()

# Create and start the update thread
#update_thread = threading.Thread(target=update_thread)
update_thread = threading.Thread(target=update_thread, args=(target_res,))
update_thread.start()

# Main Tkinter event loop
root.mainloop()

# Wait for the thread to finish
update_thread.join()
