import cv2
import numpy as np
import json
import ntpath
import os
import sys
import random
from skimage.metrics import structural_similarity as ssim


INPUT_FOLDER = ".\\input\\"
OUTPUT_FOLDER = ".\\output\\"


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


def getCollectionName(original_path):
    _tail, name = ntpath.split(original_path)
    name = name.split(".")[0]
    return name


def getCollectionFolder(name):
    return INPUT_FOLDER + name + "\\"


def saveCollection(collection):
    json_path = collection["folder"] + "collection.json"
    with open(json_path, 'w') as fp:
        json.dump(collection, fp)


def loadCollection(name):
    collection = {}
    json_path = getCollectionFolder(name) + "collection.json"
    with open(json_path, 'r') as fp:
        collection = json.load(fp)
    return collection


def cropCollection(original_path, resolution):
    name = getCollectionName(original_path)
    original_img = cv2.imread(original_path)

    if original_img.shape[0] % resolution != 0 or \
            original_img.shape[1] % resolution != 0:
        print("Image {} can't be divided in {}x{} squares!".format(
            name, resolution, resolution
        ))
        return {}

    folder = getCollectionFolder(name)
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

    frames = []
    x, y, n = 0, 0, 0
    size = int(
        (original_img.shape[0] / resolution) *
        (original_img.shape[1] / resolution))
    while x * resolution < original_img.shape[0]:
        y = 0
        while y * resolution < original_img.shape[1]:
            x1, y1 = x * resolution, y * resolution
            x2, y2 = x1 + resolution, y1 + resolution
            crop = original_img[x1: x2, y1: y2]

            filename = folder + "crop_{}x_{}y.png".format(x, y)
            cv2.imwrite(filename, crop)
            frames.append(filename)

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
        "frames": frames,
    }

    saveCollection(collection)
    return collection


def compareFrameTo(frame, collection, selection=[]):
#     print("""
# Comparing: {}
# of collection: {}
# to selection: {}
#     """.format(frame, collection["name"], selection))
#     input("")
    if collection.get("simmilarity") is None:
        collection["simmilarity"] = {}
    simmilarity = collection.get("simmilarity")
    if simmilarity.get(frame) is None:
        collection["simmilarity"][frame] = {}

    if len(selection) > 0:
        images = selection
    else:
        images = collection["frames"]

    n = 0
    img1 = cv2.imread(frame)
    for comparison in images:
        if frame in comparison:
            result = 1.0
        elif simmilarity.get(comparison) is not None and \
                simmilarity[comparison].get(frame) is not None:
            result = simmilarity[comparison][frame]
        else:
            img2 = cv2.imread(comparison)
            result = ssim(img1, img2, multichannel=True)
        simmilarity[frame][comparison] = result

        n += 1
        sys.stdout.write("\rCompared {} / {}.".format(n, len(images)))
        sys.stdout.flush()
    print("All comparisons done for {}".format(frame))

    saveCollection(collection)
    return collection


def compareSelection(selection, collection):
    n = 0
    for frame in selection:
        compareFrameTo(frame, collection, selection)

        n += 1
        print("Simmilarity matrix: {:0.2f} ( {} / {} ).".format(
                                            n / len(selection),
                                            n, len(selection)))
    return collection


def drawRandomFromCollection(collection):
    if collection.get("frames") is None:
        return {}
    i = random.randrange(0, len(collection))
    return collection["frames"][i]


def saveVideo(video, collection):
    folder = OUTPUT_FOLDER + collection["name"] + \
        "\\{}\\".format(getCollectionName(video[0]))
    if not os.path.exists(folder):
        print("Creating folder for video: {}".format(folder))
        os.makedirs(folder)

    for i in range(len(video)):
        img = cv2.imread(video[i])
        filename = folder + "frame{:05d}.png".format(i)
        print("Saving {} : {}".format(filename, video[i]))
        cv2.imwrite(filename, img)
    print("Video created!")
