import cv2
import numpy as np

def apply_dreamy_filter(image_path):
    # Load the image
    img = cv2.imread(image_path)
    
    # 1. Create a blurred version (Gaussian Blur)
    # The kernel size (21, 21) determines the "dreaminess" level
    blurred = cv2.GaussianBlur(img, (21, 21), 0)
    
    # 2. Brighten the blurred image slightly to enhance the glow
    blurred = cv2.convertScaleAbs(blurred, alpha=1.2, beta=10)
    
    # 3. Blend the original and blurred images
    # alpha is the weight of the original, beta is the weight of the glow
    dreamy_img = cv2.addWeighted(img, 0.6, blurred, 0.4, 0)
    
    return dreamy_img

# Usage
result = apply_dreamy_filter('D:/vs code data/me.jpeg')
cv2.imshow('Dreamy Effect', result)
cv2.waitKey(0)
