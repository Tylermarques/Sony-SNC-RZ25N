"""
Includes a class for initializing communication with the SNCRZ25N. Allows you to view and move the SNCRZ25N.
"""
import base64
import tkinter as tk
from threading import Thread
import json
import requests
from requests.auth import HTTPBasicAuth
from urllib.request import Request, urlopen
import numpy as np
from PIL import Image, ImageTk
import cv2


class Camera:
    # TODO Add Class documentation
    # TODO Add ability to view the Camera's feed.
    #   I have this ability in a different repository, but it makes more sense to have it as actually part of the class.
    #   The issue is that I don't want to add OpenCV to this class, so I will need to figure out a way around that.

    def __init__(self, ip, user, password, threaded=True):
        self.ip = ip
        self.user = user
        self.password = password
        self.auth = HTTPBasicAuth(user, password)
        self.threaded = threaded
        self.command_url = f"http://{ip}/command/ptzf.cgi"
        self.video_url = f"http://{ip}/image"
        self.current_pan: int = 0  # 0000/ffff is the starting preset
        self.current_tilt: int = 65535  # ffff is the starting preset
        self.current_zoom: int = 0  # 0000 is the starting preset

    def area_zoom(self, point: (), height=None, width=None):
        """
        If you'd like to do relative move/zoom on an image, you can use this function to tell the camera where in the image you'd like to focus on. This allows you to
        :param point: an x and y with origin at the center of the image. The max of x and y is the half the image size
        :param height:
        :param width:
        :return:
        """
        data = {
            "AreaZoom": f"{point[0]},{point[1]},{width if width else '0'},{height if height else '1'}"
        }
        if self.threaded:
            url = f"http://{self.ip}/command/ptzf.cgi"
            Thread(target=requests.post, args=(url,), kwargs={'data': data}).start()
        else:
            resp = requests.post(f"http://{self.ip}/command/ptzf.cgi", data=data)  # auth=self.auth)
            if resp.status_code != 204:
                raise ConnectionError

    def _relative_move(self, move_num, magnitude):
        if self.threaded:
            url = f"http://{self.ip}/command/ptzf.cgi?Relative={move_num}{magnitude}"
            Thread(target=requests.post, args=(url,), kwargs={'auth': self.auth}).start()
        else:
            resp = requests.post(f"http://{self.ip}/command/ptzf.cgi?Relative={move_num}{magnitude}")  # auth=self.auth)
            if resp.status_code != 204:
                raise ConnectionError

    def send_position_update(self):
        self.absolute_pan_tilt(self.current_pan, self.current_tilt)

    def tilt_negative(self, magnitude):
        self._relative_move("02", magnitude)

    def tilt_positive(self, magnitude):
        self._relative_move("08", magnitude)

    def pan_ccw(self, magnitude):
        self._relative_move("04", magnitude)

    def pan_cw(self, magnitude):
        self._relative_move("06", magnitude)

    def zoom_in(self, magnitude):
        self._relative_move("11", magnitude)

    def zoom_out(self, magnitude):
        self._relative_move("10", magnitude)

    def absolute_pan_tilt(self, pan_position: int, tilt_position: int, extra=0):
        data = {
            "AbsolutePanTilt": f"{'{:04x}'.format(pan_position)},{'{:04x}'.format(tilt_position)},{'{0}'.format(extra)}"
        }
        if self.threaded:
            Thread(target=requests.post, args=(self.command_url,), kwargs={'auth': self.auth, 'data': data}).start()
        else:
            resp = requests.post(f"http://{self.ip}/command/ptzf.cgi", data=data, auth=self.auth)
            if resp.status_code != 204:
                raise ConnectionError

    def absolute_pan_tilt_hex(self, hex_str: str, extra=24):
        data = {
            "AbsolutePanTilt": f"{hex_str},{'{:x}'.format(extra)}"
        }
        if self.threaded:
            Thread(target=requests.post, args=(self.command_url,), kwargs={'auth': self.auth, 'data': data}).start()
        else:
            resp = requests.post(f"http://{self.ip}/command/ptzf.cgi", data=data, auth=self.auth)
            if resp.status_code != 204:
                raise ConnectionError

    def absolute_pan(self, pan_position):
        self.absolute_pan_tilt(pan_position, 0)

    def absolute_tilt(self, tilt_position):
        self.absolute_pan_tilt(0, tilt_position)

    def absolute_zoom(self, zoom: int = 0):
        """
        Unsure if this method will work or not.

        :param zoom:
        :return:
        """
        if zoom < 0 or zoom > 65000:
            raise ValueError("zoom must be between 0 and 65000")
        data = {
            "AbsoluteZoom": f"{'{:04x}'.format(zoom)}"
        }
        if self.threaded:
            Thread(target=requests.post, args=(self.command_url,), kwargs={'auth': self.auth, 'data': data}).start()
        else:
            resp = requests.post(f"http://{self.ip}/command/ptzf.cgi", data=data, auth=self.auth)
            if resp.status_code != 204:
                raise ConnectionError

    def night_mode(self, mode: bool):
        data = {
            "DayNightMode": "manual",
            "DayNight": "on" if mode else "off"
        }
        url = f"http://{self.ip}/command/SNCRZ25N.cgi"
        if self.threaded:
            Thread(target=requests.post, args=(url,), kwargs={'auth': self.auth, 'data': data}).start()
        else:
            resp = requests.post(url, data=data, auth=self.auth)
            if resp.status_code != 204:
                raise ConnectionError

    def stream_image(self):
        # Open a sample video available in sample-videos
        vcap = cv2.VideoCapture(f'http://{self.ip}/image')
        # if not vcap.isOpened():
        #    print "File Cannot be Opened"

        while True:
            # Capture frame-by-frame
            ret, frame = vcap.read()
            # print cap.isOpened(), ret
            if frame is not None:
                # Display the resulting frame
                frame = cv2.flip(frame, 0)
                cv2.imshow('frame', frame)
                # Press q to close the video windows before it ends if you want
                if cv2.waitKey(10) & 0xFF == ord('q'):
                    break
                if cv2.waitKey(10) & 0xFF == ord('i'):
                    self.tilt_positive(2)
                if cv2.waitKey(10) & 0xFF == ord('k'):
                    self.tilt_positive(2)
            else:
                print("Frame is None")
                break


class CameraNonThreaded(Camera):
    def __init__(self, ip, user, password):
        super().__init__(ip, user, password, threaded=False)


class CameraThreaded(Camera):
    def __init__(self, ip, user, password):
        super().__init__(ip, user, password)


def typing_manual_control(camera: CameraThreaded):
    """
    Allows you to manually type in the hex of the position that the SNCRZ25N should move to.
    :param camera:
    :return:
    """

    while True:
        # cam.absolute_zoom(int(input("Zoom_num:")))
        # cam._relative_move(input("Move_num:"), "")

        camera.absolute_pan_tilt_hex(input("Hex:"))


class CameraCapture(CameraThreaded):
    def __init__(self, ip, user, password):
        super().__init__(ip, user, password)

        self.video_source = f'http://{ip}/image'
        self.vid = cv2.VideoCapture(self.video_source)
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", self.video_source)
            # Get video source width and height

        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)

    # Release the video source when the object is destroyed
    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()

    def get_frame(self):
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            if ret:
                # Return a boolean success flag and the current frame converted to BGR
                return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            else:
                return (ret, None)
        else:
            return (None, None)


class App(tk.Tk):
    def __init__(self, flipped=False):
        super().__init__()
        self.flipped = flipped
        self.attributes('-type', 'dialog')
        # open video source
        with open('../config.json', 'r') as config_file:
            config = json.load(config_file)
        self.cam = CameraCapture(config['ip'], config['user'], config['password'])

        left_frame = tk.Frame(self, borderwidth=1, border=1)
        left_frame.grid(row=0, column=0, rowspan=3, padx=2, pady=2, sticky='nsew')
        bottom_frame = tk.Frame(self, borderwidth=1, border=1)
        bottom_frame.grid(row=2, column=0, columnspan=2, padx=2, pady=2, sticky='')
        main_frame = tk.Frame(self, borderwidth=1, border=1, bg='red')
        main_frame.grid(row=0, column=1, rowspan=2, columnspan=1, padx=2, pady=2, sticky='s')
        button = tk.Button(left_frame, text='Quit', command=self.handle_quit)
        button.pack()
        button = tk.Button(left_frame, text='Reset Zoom', command=self.cam.absolute_zoom)
        button.pack()
        # # Create the "Zoom In" button
        # zoom_in_button = tk.Button(self, text="Zoom In", command=zoom_in)
        # zoom_in_button.pack()
        #
        # # Create the "Zoom Out" button
        # zoom_out_button = tk.Button(self, text="Zoom Out", command=zoom_out)
        # zoom_out_button.pack()

        self.cam_label = tk.Label(main_frame)  # , width=self.cam.width, height=self.cam.height)
        self.cam_label.bind("<Button-1>", self.image_drag_zoom_start)
        self.cam_label.bind("<ButtonRelease-1>", self.image_drag_zoom_end)

        self.cam_label.pack()
        self.delay = 15
        self.update()

    def update(self):
        ret, frame = self.cam.get_frame()
        if self.flipped:
            frame = cv2.flip(frame, 0)
            frame = cv2.flip(frame, 1)
        if ret:
            self.photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
        self.cam_label.configure(image=self.photo)
        self.after(self.delay, self.update)

    def handle_quit(self):
        self.destroy()

    def image_drag_zoom_start(self, event):
        self.drag_start = (event.x, event.y)

    def image_drag_zoom_end(self, event):
        max_px_move = 5
        x_move = abs(self.drag_start[0] - event.x)
        y_move = abs(self.drag_start[1] - event.y)
        # Translate from tkO
        relative_x = event.x - int(self.cam.width / 2)
        relative_y = event.y - int(self.cam.height / 2)
        if self.flipped:
            # relative_x = -relative_x
            relative_y = -relative_y
            relative_x = -relative_x
        if not self.drag_start:
            return
        if x_move < max_px_move and y_move < max_px_move:
            print(f"tkinter ({event.x}, {event.y})")
            print(f"Translated ({relative_x}, {relative_y})")
            self.cam.area_zoom((relative_x, relative_y))
        else:
            self.cam.area_zoom((relative_x, relative_y), width=x_move, height=y_move)


def test_basic_feed():
    with open('../config.json', 'r') as config_file:
        config = json.load(config_file)

    cam = CameraThreaded(config['ip'], config['user'], config['password'])
    try:
        # typing_manual_control(cam)
        cam.tilt_negative(0xff)
        cam.stream_image()
    except KeyboardInterrupt:
        print("")
        print("EXITING...", end="")
        cam.absolute_pan_tilt(0, 0)
        print("DONE")


if __name__ == '__main__':
    app = App(flipped=True)
    app.mainloop()
