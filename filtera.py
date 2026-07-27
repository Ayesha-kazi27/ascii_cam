import mahotas as mh
import numpy as np
import pylab as p

# Load an image
image = mh.imread('D:/vs code data/me.jpeg')

# Convert to grayscale (if applicable)
image_gray = mh.colors.rgb2gray(image)

# Simple thresholding
thresholded_image = image_gray > 125
p.imshow(thresholded_image)
p.show()