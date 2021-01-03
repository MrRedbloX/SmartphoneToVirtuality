import os
from threading import Thread
import ffmpeg

# width=1280
# height=720
width=640
height=360

t = 60
s = '{}x{}'.format(width, height)
class Recorder(Thread):
    def __init__(self,input):
        Thread.__init__(self)
        self.stream = (
            ffmpeg
            .input(input,s=s)
            .output(os.path.basename(input)+".mov",t=t)
            .global_args('-loglevel', 'error')
        )
    def run(self):
        self.stream.run()

cameras = []
for path in os.popen('ls -1 /dev/video*').read().split('\n'):
    if(path):
        ret = os.system('ffmpeg -v panic -i '+path+' -t 0.5 -f null -')
        if ret == 0:
            cameras.append(path)

print("Creating recorder")
# recorders = [Recorder(cam) for cam in cameras[1:4]]
recorders = [Recorder(cam) for cam in cameras]
print("Creating start recording")
[rec.start() for rec in recorders]
print("Waiting end of recording")
[rec.join() for rec in recorders]
print("All recorders joined")
os.system("reset")