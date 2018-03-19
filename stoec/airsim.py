from PythonClient.AirSimClient import *
import sys
import time

class notConnected(Exception): pass
class notStarted(Exception): pass

# remember Airsim uses reversed z-axis so -100 is 100 units up
DEFAULT_SPEED = 15
DEFAULT_TIMEOUT = 60

class Multirotor():
	def __init__(self):
		self.client = MultirotorClient()
		self.started = False

	def reset(self):
		try:
			self.client.reset()
		except msgpackrpc.error.TransportError:
			raise notConnected

	def connect(self):
		self.client.confirmConnection()
		self.client.enableApiControl(True)
		self.client.armDisarm(True)

	def takeoff(self):
		self.client.takeoff()

	def get_position(self):
		# get position vector
		pos_vector = self.client.getPosition()

		# return each component of position
		return pos_vector.x_val, pos_vector.y_val, pos_vector.z_val

	# function to start multirotor at specific height (default 100)
	def start(self, z = -100):
		self.reset()
		self.connect()

		self.client.takeoff()

		position = self.get_position()

		self.started = True

		# move up/down to z position
		return self.client.moveToPosition(position[0], position[1], z, \
                           		 DEFAULT_SPEED, DEFAULT_TIMEOUT, \
                           		 DrivetrainType.MaxDegreeOfFreedom, \
                           		 YawMode(False,0), -1, 0)

	# flies quadcopter in 2d plane at specified height (default 100)
	# takes vectors as list of coordinates (x, y)
	def moveOnPath(self, vectors, offset = (0, 0), z = -100, \
				   speed = DEFAULT_SPEED, timeout = DEFAULT_TIMEOUT):
		if not self.started: raise notStarted

		# construct list of vector objects for position
		path = []
		for vector in vectors:
			path.append(Vector3r(vector[0] - offset[0], vector[1] - offset[1], z))

		return self.client.moveOnPath(path, speed, timeout, \
							   		  DrivetrainType.MaxDegreeOfFreedom, \
							          YawMode(False, 0), -1, 0)
	def stop(self):
		self.client.land()
		self.client.armDisarm(False)
		self.client.enableApiControl(False)
		self.started = False

