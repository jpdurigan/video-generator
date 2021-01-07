import cv2
import glob
import numpy as np
import imagehelper as ih
from skimage.metrics import structural_similarity as ssim


folder = ".\\input\\"
images_path = glob.glob(folder + "*.png")


# for path in images_path:
#     ih.cropCollection(path, 128)


def createVideoFrom(collection_name, n=100, starting_frame=None):
    collection = ih.loadCollection(collection_name)
    if collection is None or len(collection) < 1:
        print("There is no collection!")
        return

    if starting_frame is None:
        starting_frame = ih.drawRandomFromCollection(collection)
        print("Selected {} as starting point".format(starting_frame))

    collection = ih.compareFrameTo(starting_frame, collection)

    i = n
    selection = []
    database = collection["frames"].copy()
    simmilarity = collection["simmilarity"]
    while i > 0:
        max_result = 0
        owner = ""

        for frame in database:
            if simmilarity[starting_frame][frame] > max_result and \
                        simmilarity[starting_frame][frame] != 1.0:
                max_result = simmilarity[starting_frame][frame]
                owner = frame

        selection.append(owner)
        database.remove(owner)
        i -= 1
    print("{} frames selected!".format(n))

    collection = ih.compareSelection(selection, collection)

    i = n
    video = []
    reference = starting_frame
    simmilarity = collection["simmilarity"]
    while i > 0:
        max_result = 0
        owner = ""

        for frame in database:
            if simmilarity[reference][frame] > max_result:
                max_result = simmilarity[reference][frame]
                owner = frame

        video.append(owner)
        reference = owner
        i -= 1
    print("Video done!")

    ih.saveVideo(video, collection)


createVideoFrom("fakes000004", 100, ".\\input\\fakes000004\\crop_0x_1y.png")
