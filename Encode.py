"""
Copyright (c) 2020 WistLab.Co.Ltd
This file is a part of soft compression algorithm for binary image
Encode.py - Encode images by using algorithm
"""

import cv2
import os
import PreProcess
import math
import numpy as np
import datetime
import ast
from CodeFinding import getsample
import CodeProcessing


def Golomb(m, n):
    q = math.floor(n / m) * '1' + '0'

    k = math.ceil(math.log2(m))
    c = int(math.pow(2, k)) - m
    r = n % m
    if 0 <= r < c:
        rr = format(r, 'b').zfill(k - 1)
    else:
        rr = format(r + c, 'b').zfill(k)
    value = q + rr
    return value


def Golomb_m_search(input_list, num):
    bit_need_total = []
    for m in range(1, int(math.pow(2, num))):
        bit_need = 0
        for value in input_list:
            encode = Golomb(m, value)
            bit_need = bit_need + len(encode)
        bit_need_total.append(bit_need)
    min_index = bit_need_total.index(min(bit_need_total)) + 1
    return min_index


def encode(img, height, width):
    codevalue = {}
    img_flag = np.zeros((height, width))
    for p in list(codebook.keys()):
        kernel = np.array(p, np.float32)
        kernel[kernel > 0.5] = 1
        kernel_auxiliary = np.ones(kernel.shape)
        p_height, p_width = kernel.shape
        dst = cv2.filter2D(img, -1, kernel, anchor=(0, 0), borderType=cv2.BORDER_CONSTANT)
        dst_auxiliary = cv2.filter2D(img, -1, kernel_auxiliary, anchor=(0, 0), borderType=cv2.BORDER_CONSTANT)
        can_encode_location = np.argwhere(dst == np.sum(kernel))
        for cel in can_encode_location:
            if dst_auxiliary[cel[0]][cel[1]] != dst[cel[0]][cel[1]]:
                continue
            if img_flag[cel[0]][cel[1]] == 1:
                continue
            can_encode_flag = img_flag[cel[0]: cel[0] + p_height, cel[1]: cel[1] + p_width] == 0
            if can_encode_flag.all():
                try:
                    codevalue[(cel[0], cel[1])] = codebook[p]
                    img_flag[cel[0]: cel[0] + p_height, cel[1]: cel[1] + p_width] = np.ones((p_height, p_width))
                except IndexError:
                    pass

    return codevalue


def tobinary(codevalue, height, width):
    bit_height = len(format(height, 'b'))
    bit_width = len(format(width, 'b'))
    binary = format(bit_height, 'b').zfill(4) + format(bit_width, 'b').zfill(4)
    binary = binary + format(height, 'b') + format(width, 'b')

    locations = list(codevalue.keys())
    values = list(codevalue.values())

    locations_operate = locations[:]
    for i in range(len(locations_operate)):
        locations_operate[i] = locations_operate[i][0] * width + locations_operate[i][1]
    locations_rest = locations_operate[1:]
    locations_difference = []
    for i in range(len(locations_rest)):
        locations_difference.append(locations_rest[i] - locations_operate[i])
    try:
        Golomb_m = Golomb_m_search(locations_difference[:], 5)
    except ValueError:
        Golomb_m = 0
    binary = binary + format(Golomb_m, 'b').zfill(5)
    for i in range(len(locations)):
        if i != 0:
            locations[i] = locations_difference[i - 1]
    for i in range(len(locations)):
        if i == 0:
            binary = binary + format(locations[i][0], 'b').zfill(bit_height) + \
                     format(locations[i][1], 'b').zfill(bit_width)
            binary = binary + values[i]
        else:
            location_value = Golomb(Golomb_m, locations[i])
            binary = binary + location_value
            binary = binary + values[i]

    return binary


def Encode(input_dir, output_dir, codebook_name, pixel_size, start):
    global codebook
    with open(codebook_name, 'r') as f:
        codebook = f.read()
        codebook = ast.literal_eval(codebook)

    num = 1
    PreProcess.dir_check(output_dir, emptyflag=True)
    compress_rate = []
    for f in os.listdir(input_dir):
        img_path = os.path.join(input_dir, f)
        img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE) 
        ret, img = cv2.threshold(img, 0.5, 1, cv2.THRESH_BINARY)
        height = len(img)
        width = len(img[0])

        codevalue = encode(img, height=height, width=width)
        codevalue = dict(sorted(codevalue.items(), key=lambda item: (item[0][0], item[0][1])))
        codevalue = tobinary(codevalue, height, width)
        output_path = os.path.join(output_dir, f[0:f.rfind('.bmp')]) + '.tt'
        original_pixel = height * width * len(format(pixel_size - 1, 'b'))
        final_pixel = len(codevalue)

        with open(output_path, 'wb') as g:
            g.write(codevalue.encode())
        end = datetime.datetime.now()

        compress_rate.append(original_pixel / final_pixel)

        print('\rSaving encoding results for picture %d, program has run %s, the mean compression ratio is %0.2f'
              % (num, end - start, np.mean(compress_rate)), end='')
        num = num + 1
    return np.mean(compress_rate)
