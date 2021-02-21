"""
Copyright (c) 2020 WistLab.Co.Ltd
This file is a part of soft compression algorithm for binary image
Decode.py - Decode binary stream data into the original image
"""

import cv2
import os
import PreProcess
import numpy as np
import Encode
import datetime
import ast
import math


def anti_Golomb(m, binary):
    index = binary.find('0')
    q = index
    k = math.ceil(math.log2(m))
    c = int(math.pow(2, k)) - m

    rr = int(binary[index + 1:], 2)
    rr_length = len(binary[index + 1:])
    if rr_length == k - 1:
        r = rr
    elif rr_length == k:
        r = rr - c

    value = q * m + r

    return value


def Golomb_search(input, m):
    q_index = input.find('0')
    q = q_index

    k = math.ceil(math.log2(m))
    c = int(math.pow(2, k)) - m

    try:
        rr1 = int(input[q_index + 1: q_index + 1 + k - 1], 2)
        n1 = q * m + rr1
        r1 = n1 % m

        if 0 <= r1 < c:
            value = input[0:q_index + 1 + k - 1]
            output_value = input[q_index + 1 + k - 1:]
        else:
            value = input[0:q_index + 1 + k]
            output_value = input[q_index + 1 + k:]
    except ValueError:
        value = input[0:q_index + 1 + k]
        output_value = input[q_index + 1 + k:]

    value = anti_Golomb(m, value)
    return value, output_value


def decode_search(input):
    for i in range(1, len(input) + 1):
        testencode = input[0:i]
        if testencode in decodebook.keys():
            testdecode = decodebook[testencode]
            index = i
            break
    return testdecode, input[index:]


def decode(tt):
    tt = tt.decode()
    bit_height = int(tt[0:4], 2)
    bit_width = int(tt[4:8], 2)
    height = int(tt[8:8 + bit_height], 2)
    width = int(tt[8 + bit_height:8 + bit_height + bit_width], 2)

    img = np.zeros((height, width))
    img_flag = np.zeros((height, width))
    tt = tt[8 + bit_height + bit_width:]

    Golomb_m = int(tt[0:5], 2)
    tt = tt[5:]
    if len(tt) != 0:
        first_height = int(tt[0:bit_height], 2)
        first_width = int(tt[bit_height:bit_height + bit_width], 2)
        tt = tt[bit_height + bit_width:]
        value, tt = decode_search(tt)
        shape_height = len(value)
        shape_width = len(value[0])
        img[first_height: first_height + shape_height, first_width: first_width + shape_width] = np.array(value)
        last_location = first_height * width + first_width
    while len(tt) != 0:
        if Golomb_m == 0:
            break
        location_relative, tt = Golomb_search(tt, Golomb_m)
        location = last_location + location_relative
        last_location = location
        location_height = location // width
        location_width = location % width
        [value, tt] = decode_search(tt)
        shape_height = len(value)
        shape_width = len(value[0])
        img[location_height: location_height + shape_height, location_width: location_width + shape_width] = np.array(
            value)
        img_flag[location_height: location_height + shape_height, location_width: location_width + shape_width] = 1
    return img


def fidelity(input1, input2):
    fidelity_rate = 0
    difference = input1 - input2
    for i in range(len(difference)):
        for j in range(len(difference[0])):
            fidelity_rate = fidelity_rate + pow(difference[i][j]/255, 2)
    fidelity_rate = fidelity_rate/(len(difference)*len(difference[0]))
    fidelity_rate = pow(fidelity_rate, 0.5)
    return fidelity_rate


def Decode(input_dir, output_dir, original_img_dir, codebook_name, start):
    with open(codebook_name, 'r') as f:
        codebook = f.read()
        codebook = ast.literal_eval(codebook)

    global decodebook
    decodebook = {v: k for k, v in codebook.items()}

    num = 1
    PreProcess.dir_check(output_dir, emptyflag=True)

    error_rate_total = []
    for f in os.listdir(input_dir):
        tt_path = os.path.join(input_dir, f)
        if os.path.splitext(tt_path)[1] == '.tt':
            with open(tt_path, 'rb') as g:
                tt = g.read()
            img = decode(tt)
            ret, img = cv2.threshold(img, 0.5, 255, cv2.THRESH_BINARY)
            img_original_path = os.path.join(original_img_dir, f[0:f.rfind('.tt')]) + '.bmp'
            img_original = cv2.imread(img_original_path, cv2.IMREAD_GRAYSCALE)

            output_path = os.path.join(output_dir, f[0:f.rfind('.tt')]) + '.bmp'
            cv2.imwrite(output_path, img)

            error_rate = fidelity(img_original, img)
            error_rate_total.append(error_rate)

            end = datetime.datetime.now()
            print('\rSaving decoding results for picture %d，SNR is %0.2f，the mean SNR is %0.2f, the program has run %s' % (
            num, error_rate, np.mean(error_rate_total), end - start), end='')
            num = num + 1
    return np.mean(error_rate_total)