"""
Includes a class for initializing communication with the camera. Allows you to view and move the camera.
"""

from threading import Thread
import json
import requests
from requests.auth import HTTPBasicAuth


class Camera:
    # TODO Add Class documentation
    # TODO Add ability to view the Camera's feed.
    #   I have this ability in a different repository, but it makes more sense to have it as actually part of the class.
    #   The issue is that I don't want to add OpenCV to this class, so I will need to figure out a way around that.

    def __init__(self, ip, user, password, threaded=True):
        self.ip = ip
        self.auth = HTTPBasicAuth(user, password)
        self.threaded = threaded
        self.command_url = f"http://{ip}/command/ptzf.cgi"
        self.current_pan: int = 0  # 0000/ffff is the starting preset
        self.current_tilt: int = 65535  # ffff is the starting preset
        self.current_zoom: int = 0  # 0000 is the starting preset

    def _relative_move(self, move_num, magnitude):
        if self.threaded:
            url = f"http://{self.ip}/command/ptzf.cgi?Relative={move_num}{magnitude}"
            Thread(target=requests.get, args=(url,), kwargs={'auth': self.auth}).start()
        else:
            resp = requests.get(f"http://{self.ip}/command/ptzf.cgi?Relative={move_num}{magnitude}", auth=self.auth)
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
        # print(f"AbsolutePanTilt: {data['AbsolutePanTilt']}" )
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

    def absolute_zoom(self, zoom: int):
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
        url = f"http://{self.ip}/command/camera.cgi"
        if self.threaded:
            Thread(target=requests.post, args=(url,), kwargs={'auth': self.auth, 'data': data}).start()
        else:
            resp = requests.post(url, data=data, auth=self.auth)
            if resp.status_code != 204:
                raise ConnectionError


class CameraNonThreaded(Camera):
    def __init__(self, ip, user, password):
        super().__init__(ip, user, password)


class CameraThreaded(Camera):
    def __init__(self, ip, user, password):
        super().__init__(ip, user, password)


def typing_manual_control(camera: CameraThreaded):
    """
    Allows you to manually type in the hex of the position that the camera should move to.
    :param camera:
    :return:
    """

    while True:
        # cam.absolute_zoom(int(input("Zoom_num:")))
        # cam._relative_move(input("Move_num:"), "")

        camera.absolute_pan_tilt_hex(input("Hex:"))


if __name__ == '__main__':
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)

    cam = CameraThreaded(config['ip'], config['user'], config['password'])
    try:
        typing_manual_control(cam)

    except KeyboardInterrupt:
        print("EXITING...", end="")
        cam.absolute_pan_tilt(0, 0)
        print("DONE")
