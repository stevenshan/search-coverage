'''
Script to help create probability density map from an image
Makes all pixels that are RGB(44, 2, 122) white and all other pixels
transparent black
'''

from PIL import Image
import os.path
import sys

if __name__ == "__main__":
	filename = sys.argv[1] if len(sys.argv) > 1 else ""
	flag = os.path.isfile(filename)
	while (not flag):
		filename = input("Enter path to image: ")	
		flag = os.path.isfile(filename)

	image = Image.open(filename)
	w, h = image.size
	buffer = list(image.tobytes())
	l = len(buffer)

	pixel_size = l // (w * h)

	match = [44, 2, 122, 255][:pixel_size]

	new_buffer = bytes()
	TRANSPARENT = bytes([0x00, 0x00, 0x00, 0x00])

	counter = 0
	for i in range(0, l, pixel_size):
		if buffer[i : i + pixel_size] == match:
			new_buffer += bytes([0xFF, 0xFF, 0xFF, 0xFF])
		else:
			new_buffer += TRANSPARENT

		if (i % (l // 20) == 0):
			print(str(counter) + "% complete")
			counter += 5

	img = Image.frombytes("RGBA", (w, h), new_buffer)
	file = os.path.splitext(filename)
	img.save(file[0] + ".mask" + file[1])
