"""
Copyright (c) 2020 WistLab.Co.Ltd
This file is a part of soft compression algorithm for binary image
PreProcess.py - Generate the training set and testing set
"""

import os
import shutil
import cv2
import struct
import numpy as np


def dir_check(filepath, printflag=True, emptyflag=False):
    """
    Judge whether the folder exists. If it exists, empty all its files and subfolders according to the emptyflag. if
    not, create it
    :param filepath:
    :return:
    """
    if os.path.exists(filepath) and emptyflag:
        del_file(filepath)
    if not os.path.exists(filepath):
        os.makedirs(filepath)
    if printflag:
        print('Output directory %s has been emptied and created' % filepath)


def del_file(filepath):
    """
    Del all the files in the filepath
    :param filepath: filepath
    :return:
    """
    del_list = os.listdir(filepath)
    for f in del_list:
        file_path = os.path.join(filepath, f)
        if os.path.isfile(file_path):
            os.remove(file_path)

        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)


def decode_idx3_ubyte(idx3_ubyte_file):
    with open(idx3_ubyte_file, 'rb') as f:
        print('Parsing files: ', idx3_ubyte_file)
        fb_data = f.read()

    offset = 0
    fmt_header = '>iiii'
    magic_number, num_images, num_rows, num_cols = struct.unpack_from(fmt_header, fb_data, offset)
    offset += struct.calcsize(fmt_header)
    fmt_image = '>' + str(num_rows * num_cols) + 'B'

    images = np.empty((num_images, num_rows, num_cols))
    for i in range(num_images):
        im = struct.unpack_from(fmt_image, fb_data, offset)
        images[i] = np.array(im).reshape((num_rows, num_cols))
        offset += struct.calcsize(fmt_image)
    return images


def decode_idx1_ubyte(idx1_ubyte_file):
    with open(idx1_ubyte_file, 'rb') as f:
        print('Parsing files: ', idx1_ubyte_file)
        fb_data = f.read()

    offset = 0
    fmt_header = '>ii'
    magic_number, label_num = struct.unpack_from(fmt_header, fb_data, offset)
    offset += struct.calcsize(fmt_header)
    labels = []

    fmt_label = '>B'
    for i in range(label_num):
        labels.append(struct.unpack_from(fmt_label, fb_data, offset)[0])
        offset += struct.calcsize(fmt_label)
    return labels


def export_img(exp_dir, img_ubyte, lable_ubyte):
    """
    Create the dataset
    """
    images = decode_idx3_ubyte(img_ubyte)
    labels = decode_idx1_ubyte(lable_ubyte)

    nums = len(labels)
    for i in range(nums):
        img_dir = os.path.join(exp_dir, str(labels[i]))
        dir_check(img_dir, printflag=False)
        img_file = os.path.join(img_dir, str(i) + '.bmp')
        imarr = images[i]
        ret, binary = cv2.threshold(imarr, 127, 255, cv2.THRESH_BINARY)
        cv2.imwrite(img_file, binary)


def parser_mnist_data(input_dir, output_dir):
    """
    Parsing MNIST dataset
    :param input_dir: input folder
    :param output_dir: output folder
    :return:None
    """
    train_dir = output_dir[0]
    train_img_ubyte = os.path.join(input_dir, 'train-images.idx3-ubyte')
    train_label_ubyte = os.path.join(input_dir, 'train-labels.idx1-ubyte')
    export_img(train_dir, train_img_ubyte, train_label_ubyte)

    test_dir = output_dir[1]
    test_img_ubyte = os.path.join(input_dir, 't10k-images.idx3-ubyte')
    test_label_ubyte = os.path.join(input_dir, 't10k-labels.idx1-ubyte')
    export_img(test_dir, test_img_ubyte, test_label_ubyte)


def PreProcess(dataset):
    if dataset == 'MNIST':
        # Define input and output folder
        input_dir = 'Dataset/MNIST'
        output_dir = ['train', 'test']

        # Make output folder exist and empty
        dir_check(output_dir[0], emptyflag=True)
        dir_check(output_dir[1], emptyflag=True)

        # Parsing MNIST dataset
        parser_mnist_data(input_dir, output_dir)