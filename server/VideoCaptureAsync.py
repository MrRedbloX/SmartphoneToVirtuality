import threading
import cv2
from time import time

import asyncio

class VideoCaptureAsync:
    def __init__(self, src=0, width=640, height=480,framerate=20,oversample=8):
        self.src = src
        self.cap = cv2.VideoCapture(self.src)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.cap.set(cv2.CAP_PROP_FPS, framerate)

        self.grabbed, self.frame = self.cap.read()
        self.started = False
        self.read_lock = threading.Lock()

        self.framerate = framerate
        self.last_cap = time()
        self.oversample = oversample

    def set(self, var1, var2):
        self.cap.set(var1, var2)

    def start(self):
        if self.started:
            print('[!] Threaded video capturing has already been started.')
            return None
        self.started = True
        self.thread = threading.Thread(target=self.planUpdate, args=())
        self.thread.start()
        return self

    def planUpdate(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        task = loop.create_task(self.update())
        try:
            loop.run_until_complete(task)
        except asyncio.CancelledError:
            pass
        finally:
            loop.close()

    @asyncio.coroutine
    def update(self):
        while self.started:
            t = time()
            with self.read_lock:
                cap = t - self.last_cap >= 1/self.framerate
            if cap:
                grabbed, frame = self.cap.read()
                t = time()
            with self.read_lock:
                if cap:
                    self.last_cap = t
                    self.grabbed = grabbed
                    self.frame = frame
                yield from asyncio.sleep(1.0/self.framerate/self.oversample)

    def read(self):
        with self.read_lock:
            grabbed = self.grabbed
            frame = self.frame.copy() if grabbed else self.frame
        return grabbed, frame

    def stop(self):
        self.started = False
        self.thread.join()

    def __exit__(self, exec_type, exc_value, traceback):
        self.cap.release()
