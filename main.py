########################################################################################################################
# Soft Compression：main
# Procedure steps：Preprocess, CodeFinding, CodeProcessing, Encode, Decode
# Output is compression ration and error rate
########################################################################################################################

import PreProcess
import CodeFinding
import CodeProcessing
import Encode
import Decode
import os
import numpy as np
import datetime

if __name__ == '__main__':

    input_dir = ['train', 'test']  # input folder
    output_dir = ['test_encode', 'test_decode']  # output folder
    frequency_dir = 'frequency'  # the folder to save frequency
    codebook_dir = 'codebook'  # the folder to save codbook

    pixel_size = 2  # pixel value
    shape_height = [1, 28]  # height range of rectangle
    shape_width = [1, 28]  # width range of rectangle

    compress_rate = np.zeros((10, 10))  # compression ratio
    error_rate = np.ones((10, 10))  # error ratio

    start = datetime.datetime.now()  # starting time

    # PreProcess
    PreProcess.PreProcess('MNIST')
    # Empty folders
    PreProcess.dir_check(frequency_dir, emptyflag=True)
    PreProcess.dir_check(codebook_dir, emptyflag=True)
    PreProcess.dir_check(output_dir[0], emptyflag=True)
    PreProcess.dir_check(output_dir[1], emptyflag=True)

    # Frequency
    for f in os.listdir(input_dir[0]):
        process_dir = os.path.join(input_dir[0], f)
        print('\nSearching for folder %s:' % process_dir)
        CodeFinding.CodeFinding(process_dir, shape_height, shape_width, frequency_dir, start)

    # Codebook Process
    for f in os.listdir(frequency_dir):
        process_frequency = os.path.join(frequency_dir, f)
        print('\nProcessing for codebook %s：' % process_frequency)
        CodeProcessing.CodeProcessing(process_frequency, codebook_dir)

    # Encode
    for f in os.listdir(codebook_dir):
        codebook_name = os.path.join(codebook_dir, f)
        index1 = f.rfind('_')
        index2 = f.rfind('.txt')
        codebook_num = int(f[index1+1:index2])
        for g in os.listdir(input_dir[1]):
            encode_dir = os.path.join(input_dir[1], g)
            test_encode_dir = os.path.join(output_dir[0], f[0:f.rfind('.txt')], g)
            print('\n\nEncode:%s-----%s:' % (codebook_num, encode_dir))
            rate = Encode.Encode(encode_dir, test_encode_dir, codebook_name, pixel_size, start)
            compress_rate[codebook_num][int(g)] = rate

    # Decode：
    for f in os.listdir(output_dir[0]):
        codebook_name = os.path.join(codebook_dir, f) + '.txt'
        index1 = codebook_name.rfind('_')
        index2 = codebook_name.rfind('.txt')
        codebook_num = int(codebook_name[index1 + 1:index2])
        for g in os.listdir(os.path.join(output_dir[0], f)):
            decode_dir = os.path.join(output_dir[0], f, g)
            test_decode_dir = os.path.join(output_dir[1], f, g)
            original_img_dir = os.path.join(input_dir[1], g)
            print('\n\nDecode:%s:' % decode_dir)
            rate = Decode.Decode(decode_dir, test_decode_dir, original_img_dir, codebook_name, start)
            error_rate[codebook_num][int(g)] = rate

    # Save compression ratio
    with open('compress_rate.txt', 'w') as g:
        g.write(str(compress_rate))
    # Save error ratio
    with open('error_rate.txt', 'w') as g:
        g.write(str(error_rate))