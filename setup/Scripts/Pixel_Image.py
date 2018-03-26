DEFAULT_DIMENSION = 256

class Pixel:
    TRANSPARENT = (0, 0, 0, 0)
    WHITE = (255, 255, 255, 255)
    BLACK = (0, 0, 0, 255)
    RED = (255, 0, 0, 255)
    GREEN = (0, 255, 0, 255)
    BLUE = (0, 0, 255, 255)

class Image:
    # initialize an image as byte array with given pixel value
    @staticmethod
    def init(width = DEFAULT_DIMENSION, height = DEFAULT_DIMENSION, \
             pixel = Pixel.WHITE):
        img = bytes()
        for i in range(height):
            img += bytes(list(pixel)) * width
        return img

    # return an image with pixel at (i, j) replaced with given pixel
    @staticmethod
    def replace_pixel(img, i, j, width, pixel):
        return img[:(i * width + j) * 4] + \
               bytes(list(pixel)) + \
               img[(i * width + j + 1) * 4:]

    def __init__(self, width = DEFAULT_DIMENSION, height = DEFAULT_DIMENSION, \
                 pixel = Pixel.WHITE):
        self.image = self.init(width, height, pixel)
        self.width = width
        self.height = height

    def set_pixel(self, i, j, pixel):
        if i >= 0 and i < self.height and j >= 0 and j < self.width:
            self.image = self.replace_pixel(self.image, i, j, self.width, pixel)

    def draw_line(self, coord1, coord2, pixel = Pixel.BLACK):
        # starting point of line
        i, j = coord1[0], coord1[1]

        # length of line
        dist = int(round(math.sqrt((coord2[0] - coord1[0]) ** 2 + 
                                   (coord2[1] - coord1[1]) ** 2)))

        slope = (coord2[0] - coord1[0]) / dist, (coord2[1] - coord1[1]) / dist
        # draw line
        for k in range(dist):
            self.set_pixel(round(i), round(j), pixel)
            i += slope[0]
            j += slope[1]