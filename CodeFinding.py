########################################################################################################################
# Soft Compression：module-2
# Aim: search the frequency of the set of shapes
########################################################################################################################

import cv2
import os
import datetime
import numpy as np
import math


def renew_codebook(sample):
    """
    Update the frequency of each shape in the codebook. If there is a key in the codebook, add 1. If not, create it.
    :param sample: sample value
    :return: none
    """
    global codebook
    sample_judge = np.array(sample) == 0
    if (np.sum(sample_judge, axis=0) <= sample_judge.shape[0]/2).all() \
            and (np.sum(sample_judge, axis=1) <= sample_judge.shape[1]/2).all():
        if sample in codebook.keys():
            new_value = codebook[sample] + 1  # Get the original dictionary value and add 1
            codebook[sample] = new_value  # Assign a new dictionary value
        else:
            codebook[sample] = 1


def getsample(shape_height, shape_width, img, i, j):
    """
    Get the image and shape
    :param shape_height: the height of an image
    :param shape_width: the width of an image
    :param i: the height location of an image
    :param j: the width location of an image
    :return:
    """
    height = len(img)  # Get the height of an image
    width = len(img[0])  # Get the width of an image
    if i + shape_height < height and j + shape_width < width:  # Judge whether to cross the boundary
        sample = img[i:i + shape_height, j:j + shape_width]
        sample = tuple(map(tuple, sample))
        return True, sample  # Get the sample value
    else:
        return False, None


def search_code(img, shape_height, shape_width):
    height = len(img)  # Get the height of an image
    width = len(img[0])  # Get the width of an image
    for i in range(height):
        for j in range(width):
            for u in range(shape_height[0], shape_height[1] + 1):
                for v in range(shape_width[0], shape_width[1] + 1):
                    [FLAG, sample] = getsample(u, v, img, i, j)  # Get whether there is a codebook and the sample value
                    if FLAG:
                        renew_codebook(sample)  # The statistical character


def codebookcompress(degree1, degree2, degree3):
    """
    Del shapes with low frequency
   :param degree1: Compression degree 1
   :param degree2: Compression degree 2
   :param degree2: Compression degree 3
   :return:
   """
    global codebook
    num = 0
    for key in list(codebook.keys()):
        if codebook[key] <= degree1 * degree2 * degree3:
            del codebook[key]  # Del
            num = num + 1
    return num


def CodeFinding(input_dir, shape_height, shape_width, output_dir, start):

    batch_size = 10  # the size of a batch
    round_num = 0  # Record the rounds

    global codebook  # Create the codebook
    codebook = {}

    img_path_total = os.listdir(input_dir)  # Record all pictures' relative address

    round_total = math.ceil(len(img_path_total) / batch_size)  # Total number of rounds of image searching
    for i in range(round_total):
        # Identify the image address in a batch
        start_num = batch_size * round_num  # Determine the starting position in a batch
        end_num = batch_size * (round_num + 1)  # Determine the ending position in a batch
        if batch_size * (round_num + 1) < len(img_path_total):
            img_path_batch = img_path_total[start_num: end_num]
        else:
            img_path_batch = img_path_total[start_num:]

        # Update image search codebook
        for f in img_path_batch:
            img_path = os.path.join(input_dir, f)
            img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            search_code(img, shape_height, shape_width)
        # Delete codebook with low frequency
        delnum = codebookcompress(degree1=0.01, degree2=round_num + 1, degree3=batch_size)

        end = datetime.datetime.now()
        print('\rThe %d round of searching has been completed, the total number of codewords is %d，the program has run %s' % (round_num + 1, len(codebook), delnum, end - start),
              end=' ')
        round_num = round_num + 1

    codebook = dict(sorted(codebook.items(), key=lambda item: item[1], reverse=True))  # The nodes are sorted from large to small according to frequency

    output_name = os.path.join(output_dir, 'frequency') + '_' + input_dir[input_dir.rfind('\\') + 1:] + '.txt'
    with open(output_name, 'w') as f:
        f.write(str(codebook))
    print('\nThe searching has been completed，codebook has been saved as %s' % output_name)
