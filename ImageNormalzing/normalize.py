import cv2
import numpy as np

# Read the 8-bit image
img = cv2.imread('original.tif', cv2.IMREAD_UNCHANGED)

# Convert to 16-bit
img_16bit = np.uint16(img) * 256  # Scale values to 16-bit range

# Save the 16-bit image
cv2.imwrite('image_16bit.tiff', img_16bit)