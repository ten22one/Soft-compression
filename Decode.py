########################################################################################################################
# Soft Compression：module-5
# Aim: decode the compressed date to restore the original image
########################################################################################################################

import cv2
import os
import PreProcess
import numpy as np
import Encode
import datetime
import ast


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
    height = int(tt[8:8 + bit_height], 2) + 1
    width = int(tt[8 + bit_height:8 + bit_height + bit_width], 2) + 1
    img = np.zeros((height, width))
    img_flag = np.zeros((height, width))
    tt = tt[8 + bit_height + bit_width:]

    while len(tt) != 0:
        location_height = int(tt[0:bit_height], 2)
        location_width = int(tt[bit_height:bit_height + bit_width], 2)
        tt = tt[bit_height + bit_width:]
        [value, tt] = decode_search(input=tt)
        shape_height = len(value)
        shape_width = len(value[0])
        img[location_height: location_height + shape_height, location_width: location_width + shape_width] = np.array(
            value)
        img_flag[location_height: location_height + shape_height, location_width: location_width + shape_width] = 1
    [num_one, num_zero] = Encode.inspect(img_flag)
    return img, [num_one, num_zero]


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
            [img, info] = decode(tt)

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