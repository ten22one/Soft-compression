########################################################################################################################
# Soft Compression：module-4
# Aim: Encode the image
########################################################################################################################

import cv2
import os
import PreProcess
import numpy as np
import datetime
import ast
from CodeFinding import getsample
import CodeProcessing


def encode(img, height, width):
    codevalue = {}
    codeshow = {}
    img_flag = np.zeros((height, width))
    for i in range(height):
        for j in range(width):
            if img_flag[i][j] == 1:
                continue
            for key in codebook.keys():
                if img[i][j] != key[0][0]:
                    continue
                shape_height = len(key)
                shape_width = len(key[0])
                [FLAG, sample] = getsample(shape_height, shape_width, img, i, j)
                if FLAG and (img_flag[i: i + shape_height, j: j + shape_width] == 0).all():
                    if CodeProcessing.similarity(sample, key, rate=0):
                        codevalue[(i, j)] = codebook[key]
                        codeshow[(i, j)] = key
                        img_flag[i: i + shape_height, j: j + shape_width] = np.ones((shape_height, shape_width))
                        break
    [num_one, num_zero] = inspect(img_flag)

    return codevalue, codeshow, [num_one, num_zero]


def inspect(input):
    num1 = 0
    num2 = 0
    for i in range(len(input)):
        for j in range(len(input[0])):
            if input[i][j] == 1:
                num1 = num1 + 1
            elif input[i][j] == 0:
                num2 = num2 + 1
    return num1, num2


def tobinary(codevalue, height, width):
    bit_height = len(format(height, 'b'))
    bit_width = len(format(width, 'b'))
    binary = format(bit_height, 'b').zfill(4) + format(bit_width, 'b').zfill(4)
    binary = binary + format(height, 'b') + format(width, 'b')

    for item in codevalue.items():
        [location, value] = item
        binary = binary + format(location[0], 'b').zfill(bit_height) + format(location[1], 'b').zfill(bit_width)
        binary = binary + value
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
        img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)  # 读入图片
        height = len(img)
        width = len(img[0])

        [codevalue, codeshow, info] = encode(img, height=height, width=width)

        codevalue = tobinary(codevalue, height-1, width-1)
        output_path = os.path.join(output_dir, f[0:f.rfind('.bmp')]) + '.tt'
        original_pixel = height * width * len(format(pixel_size-1, 'b'))
        final_pixel = len(codevalue)

        with open(output_path, 'wb') as g:
             g.write(codevalue.encode())
        end = datetime.datetime.now()

        compress_rate.append(original_pixel/final_pixel)

        print('\rSaving encoding results for picture %d, program has run%s, the mean compression ratio is %0.2f'
              % (num, end-start, np.mean(compress_rate)), end='')
        num = num + 1
    return np.mean(compress_rate)