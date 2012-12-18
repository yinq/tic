#! /usr/bin/env python

import web
import pygame
import pygame.camera
import serial
from webcam import CameraCapture

web.config.debug = False

urls = (
	'/', 'index',
	'/stream', 'stream',
	'/control', 'control'
)

app = web.application(urls, globals())
session = web.session.Session(app, web.session.DiskStore('sessions'), initializer={'angle': 512, 'camera_stat' : False})


class index:
	def GET(self):
		render = web.template.render('templates/')
		return render.index()

class control:
	def __init__(self):
		self.ser = serial.Serial('/dev/ttyUSB0', 9600)

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
		self.ser.write('%s#' % session.angle)

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
	

if __name__ == "__main__":
	pygame.init()
	pygame.camera.init()
	app.run()
