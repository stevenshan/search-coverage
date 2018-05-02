from PythonClient.AirSimClient import *
import sys
import time
import _thread as thread
import config

class notConnected(Exception): pass
class notStarted(Exception): pass

# remember Airsim uses reversed z-axis so -100 is 100 units up
DEFAULT_SPEED = 5
DEFAULT_TIMEOUT = 60
DEFAULT_PATHLENGTH = 5

def tick(self):
    index = 0
    while (True):
        index += 1
        if (len(self.moveQueue) != 0):
            path = self.moveQueue[0:100]
            self.client.moveOnPath(path, DEFAULT_SPEED, DEFAULT_TIMEOUT, \
                DrivetrainType.MaxDegreeOfFreedom, YawMode(False, 0), -1, 0)
            self.moveQueue = self.moveQueue[100:]

            response = self.getImage();
            # get numpy array
            img1d = np.fromstring(response.image_data_uint8, dtype=np.uint8) 

            # reshape array to 4 channel image array H X W X 4
            img_rgba = img1d.reshape(response.height, response.width, 4)  

            # original image is fliped vertically
            img_rgba = np.flipud(img_rgba)

            # write to png 
            self.client.write_png(config.get_image_dir() + str(index) + ".png", img_rgba) 
        else:
            time.sleep(0.2)

class Multirotor():
    def __init__(self, scale=(1.0, 1.0)):
        self.client = MultirotorClient()
        self.started = False
        self.scale = scale
        self.moveQueue = []
        thread.start_new_thread(tick, (self,))

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

    def getImage(self):
        request = [ImageRequest(1, AirSimImageType.Scene, False, False)]
        responses = self.client.simGetImages(request)
        response = responses[0]
        return response

    def get_position(self):
        # get position vector
        pos_vector = self.client.getPosition()

        # return each component of position
        return pos_vector.x_val, pos_vector.y_val, pos_vector.z_val

    # function to start multirotor at specific height (default 100)
    def start(self, z = -30):
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

    # flies quadcopter in 2d plane at specified height (default 50)
    # takes vectors as list of coordinates (x, y)
    def moveOnPath(self, vectors, offset = (0, 0), z = -30):
        if not self.started: raise notStarted

        # construct list of vector objects for position
        for vector in vectors:
            self.moveQueue.append(Vector3r((vector[1] - offset[0]) * self.scale[0],  \
                                 (vector[0] - offset[1]) * self.scale[1], z))

        return len(self.moveQueue)

    def getQueueLength(self):
        return len(self.moveQueue)

    # synchronous version of moveOnPath
    def moveOnPathSync(self, vectors, offset = (0, 0), z = -30, \
                   speed = DEFAULT_SPEED, timeout = DEFAULT_TIMEOUT):
        if not self.started: raise notStarted

        # construct list of vector objects for position
        path = []
        for vector in vectors:
            path.append(Vector3r((vector[1] - offset[0]) * self.scale[0],  \
                                 (vector[0] - offset[1]) * self.scale[1], z))

        return self.client.moveOnPath(path, speed, timeout, \
                                      DrivetrainType.MaxDegreeOfFreedom, \
                                      YawMode(False, 0), -1, 0)
        
    def stop(self):
        self.client.land()
        self.client.armDisarm(False)
        self.client.enableApiControl(False)
        self.started = False

