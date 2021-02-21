"""
Copyright (c) 2020 WistLab.Co.Ltd
This file is a part of soft compression algorithm for binary image
CodeProcessing.py - Generate the codebook according to the frequency
"""

import os
import numpy as np
import ast


class Node:
    def __init__(self, freq):
        self.left = None
        self.right = None
        self.father = None
        self.freq = freq

    def isLeft(self):
        return self.father.left == self


def createNodes(freqs):
    return [Node(freq) for freq in freqs]


# Create Huffman tree
def createHuffmanTree(nodes):
    num = 1
    queue = nodes[:]
    while len(queue) > 1:
        queue.sort(key=lambda item: item.freq)
        node_left = queue.pop(0)
        node_right = queue.pop(0)
        node_father = Node(node_left.freq + node_right.freq)
        num = num + 1
        node_father.left = node_left
        node_father.right = node_right
        node_left.father = node_father
        node_right.father = node_father
        queue.append(node_father)
    queue[0].father = None
    return queue[0]


# Huffman-coding
def huffmanEncoding(nodes, root):
    codes = [''] * len(nodes)
    for i in range(len(nodes)):
        node_tmp = nodes[i]
        while node_tmp != root:
            if node_tmp.isLeft():
                codes[i] = '0' + codes[i]
            else:
                codes[i] = '1' + codes[i]
            node_tmp = node_tmp.father
    return codes


def codebook_compress(codebook, rate=8):
   new_codebook = {}
   new_codebook[list(codebook.keys())[0]] = 0
   for key1 in list(codebook.keys()):
       for key2 in list(new_codebook.keys()):
           if similarity(codebook[key1], new_codebook[key2], rate):
               new_codebook[key2] = new_codebook[key2] + codebook[key1]
           else:
               new_codebook[key2] = codebook[key1]
   return new_codebook


def similarity(input1, input2, rate=8):
    input1 = np.array(input1)
    input2 = np.array(input2)
    if input1.shape != input2.shape:
        return False
    else:
        difference = abs(input1 - input2)
        return (difference <= rate).all()


def CodeProcessing(frequency_name, output_dir):

    with open(frequency_name, 'r') as f:
        codebook = f.read()
        codebook = ast.literal_eval(codebook)
    for key in codebook.keys():
        midvalue = codebook[key] * len(key) * len(key[0])
        codebook[key] = midvalue
    codebook = dict(sorted(codebook.items(), key=lambda item: item[1], reverse=True))

    chars = list(codebook.keys())
    freqs = list(codebook.values())

    nodes = createNodes(freqs)
    root = createHuffmanTree(nodes)
    codes = huffmanEncoding(nodes, root)

    codebook = dict(zip(chars, codes))
    codebook = dict(sorted(codebook.items(), key=lambda item: np.sum(np.array(item[0]) != 0), reverse=True))
    output_name = os.path.join(output_dir, 'codebook') + '_' + frequency_name[frequency_name.rfind('_') + 1:]

    with open(output_name, 'w') as f:
        f.write(str(codebook))
    print('Huffman-coding has been completed，codebook was saved as %s' % output_name)
