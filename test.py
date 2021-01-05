import cv2
import glob
import numpy as np
import imagehelper as ih
from skimage.metrics import structural_similarity as ssim


folder = ".\\input\\"
images_path = glob.glob(folder + "*.png")


for path in images_path:
    ih.cropCollection(path, 128)
