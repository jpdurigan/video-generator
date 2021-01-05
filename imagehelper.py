import cv2
import numpy as np
import json
import ntpath
import os
import sys
from skimage.metrics import structural_similarity as ssim


INPUT_FOLDER = ".\\input\\"


def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")




def cropCollection(original_path, resolution):
    _tail, name = ntpath.split(original_path)
    name = name.split(".")[0]

    original_img = cv2.imread(original_path)
    if original_img.shape[0] % resolution != 0 or \
                original_img.shape[1] % resolution != 0:
        print("Image {} can't be divided in {}x{} squares!".format(
            name, resolution, resolution
        ))
        return {}
    

    folder = INPUT_FOLDER + name + "\\"
    if not os.path.exists(folder):
        print("Creating folder for collection {}".format(name))
        os.makedirs(folder)
    else:
        override = query_yes_no("Collection already exists. Override it?")
        if not override:
            i = 1
            try_name = name + "_%02d" % i
            try_folder = INPUT_FOLDER + try_name + "\\"
            while os.path.exists(try_folder):
                i += 1
                try_name = name + "_%02d" % i
                try_folder = INPUT_FOLDER + try_name + "\\"
            
            print("Creating folder for collection {}".format(try_name))
            os.makedirs(try_folder)
            name, folder = try_name, try_folder
    

    x, y, n = 0, 0, 0
    size = int((original_img.shape[0] / resolution) * (original_img.shape[1] / resolution))
    while x * resolution < original_img.shape[0]:
        y = 0
        while y * resolution < original_img.shape[1]:
            x1, y1 = x * resolution, y * resolution
            x2, y2 = x1 + resolution, y1 + resolution
            crop = original_img[x1 : x2, y1 : y2]

            filename = folder + "crop_{}x_{}y.png".format(x, y)
            cv2.imwrite(filename, crop)

            y += 1
            n += 1
            sys.stdout.write("\rCropped {} / {}.".format(n, size))
            sys.stdout.flush()
        x += 1
    
    print("All images cropped!")


    collection = {
        "name": name,
        "folder": folder,
        "size": size,
        "resolution": resolution,

    }

    return collection