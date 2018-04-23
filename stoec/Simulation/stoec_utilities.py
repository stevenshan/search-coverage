import numpy as np
import matplotlib.pyplot as plt
import io
from PIL import Image
from functools import reduce
import math

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

DEFAULT_WIDGET_DIMENSION = 256

class Utilities():
    trajectory_initialized = False
    trajectory_RGB = []

    # convert utility matrix with probability distribution to RGBA byte string
    @staticmethod
    def getUtilityRGB(utility):

        utility = np.copy(utility)
        x_dim, y_dim = utility.shape
        utility_max, utility_min = utility.max(), utility.min() 
        utility_diff = utility_max - utility_min

        def toPixel_helper(x, diff):
            try:
                delta = (x / diff)
                pixel = [0x00, 0x00, 0x00]
                pixel = pixel + [int(delta * 255)]
                pixel = [int(255 - delta * 255)] * 3 + [0xFF]
                return pixel 
            except: # handle division by zero
                return [0x00] * 4
        toPixel = lambda x: bytes(toPixel_helper(x - utility_min, utility_diff))

        # map toPixel to utility matrix and flatten
        heatmap = bytes()
        for y in range(y_dim - 1, -1, -1):
            for x in range(x_dim):
                heatmap += toPixel(utility[y, x])

        buffer = Image.frombytes("RGBA", utility.shape, heatmap)
        n = DEFAULT_WIDGET_DIMENSION
        buffer = buffer.resize((n, n), Image.ANTIALIAS)

        return buffer.tobytes()

    def initTrajectoryRGB(self):
        self.trajectory_initialized = True
        pixel = bytes([0xFF, 0xFF, 0xFF, 0xFF])
        self.trajectory_RGB = []
        for i in range(DEFAULT_WIDGET_DIMENSION):
            self.trajectory_RGB += [pixel] * DEFAULT_WIDGET_DIMENSION

    def updateTrajectoryRGB(self, vectors, xrange, yrange):
        if (not self.trajectory_initialized):
            self.initTrajectoryRGB()

        xmin, xmax = xrange
        xrange = xmax - xmin
        ymin, ymax = yrange
        yrange = ymax - ymin

        n = DEFAULT_WIDGET_DIMENSION

        def set_pixel(i, j):
            i = int(((i - xmin) / xrange) * n)
            j = int(((ymax - j) / yrange) * n)

            index = j * n + i
            try:
                self.trajectory_RGB[index] = bytes([0x00, 0x00, 0x00, 0xFF])
            except:
                pass

        for vector in vectors:
            x, y = vector[0], vector[1]
            set_pixel(x, y)

    def getTrajectoryRGB(self):
        return reduce((lambda x, y: x + y), self.trajectory_RGB)

    @staticmethod
    def displayImage(rgba):
        l = len(rgba)
        n = int(math.sqrt(l // 4))
        img = Image.frombytes("RGBA", (n, n), rgba) 
        img.show()

    @staticmethod
    def saveImage(rgba, location):
        l = len(rgba)
        n = int(math.sqrt(l // 4))
        img = Image.frombytes("RGBA", (n, n), rgba) 
        img.save(location)

    def displayTrajectory(self):
        n = DEFAULT_WIDGET_DIMENSION
        buffer = Image.frombytes("RGBA", (n, n), self.getTrajectoryRGB())
        buffer.show()
