#! /usr/bin/env python

import web
import pygame
import pygame.camera
import serial
import subprocess
from webcam import CameraCapture

LAMP_CMD = '/home/yinq/proj/tic/rf-control/dist/Debug/GNU_Arm-Linux-x86/rf24bb'

web.config.debug = False

urls = (
  '/', 'index',
  '/stream', 'stream',
  '/control', 'control',
  '/lamp', 'Lamp'
)

app = web.application(urls, globals())
session = web.session.Session(app, web.session.DiskStore('sessions'), initializer={'angle': 512, 'camera_stat' : False})

render = web.template.render('templates/')

class index:
  def GET(self):
    lamp_status = int(subprocess.check_output([LAMP_CMD, '2'])) 
    return render.index(lamp_status)

class control:
  #def __init__(self):
    #self.ser = serial.Serial('/dev/ttyUSB0', 9600)

  def GET(self):
    i = web.input(direc=None,stat=None)
    print 'GET = ' + str(i.direc) + ', angle = ' + str(session.angle)
    if i.direc == 'left':
      if session.angle - 20 > 0:
        session.angle = session.angle - 20
    elif i.direc == 'right':
      if session.angle + 20 < 1023:
        session.angle = session.angle + 20
    elif i.direc == 'center':
      session.angle = 512
    subprocess.call([LAMP_CMD, '3%s' % session.angle])

class stream:
  def __init__(self):
    self.camera = CameraCapture("/dev/video0", (320,240), 8) 

  def GET(self):
    i = web.input(stat=None)
    print 'GET = ' + str(i.stat)
    session.camera_stat = True if i.stat == 'open' else False

    web.header('Access-Control-Allow-Origin', '*')
    web.header('Content-Type', 'multipart/x-mixed-replace;boundary=pi.webcam')
 
    frame_id = self.camera.frame_count

    #while session.camera_stat:
    while True: 
      self.camera.frame_available.acquire()
      while frame_id == self.camera.frame_count:
        self.camera.frame_available.wait()
      self.camera.frame_available.release()
        
      frame_id = self.camera.frame_count
      response = "Content-type: image/jpeg\n\n"
      response = response + self.camera.get_image()
      response = response + "\n--pi.webcam\n"
      yield response 

class Lamp:

  def GET(self):
    cur = int(web.input(cur='').cur)
    subprocess.call([LAMP_CMD, str(1 - cur)])
    return 'OK'
  

if __name__ == "__main__":
  pygame.init()
  pygame.camera.init()
  app.run()
