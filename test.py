import cv2
import glob
import numpy as np
from skimage.metrics import structural_similarity as ssim

folder = ".\\input\\fakes000004\\"
images_path = glob.glob(folder + "*.png")

# print(images_path)

for path1 in images_path:
    for path2 in images_path:
        img1 = cv2.imread(path1)
        img2 = cv2.imread(path2)

        vis = np.concatenate((img1, img2), axis=1)
        window = (path1.replace(folder, "")).replace(".png", "") + " x " + (path2.replace(folder, "")).replace(".png", "")
        s = ssim(img1, img2, multichannel=True)

        print("""
{}:
SSIM = {}
        """.format(window, s)) 

        cv2.imshow(window, vis)
        cv2.waitKey(0)
