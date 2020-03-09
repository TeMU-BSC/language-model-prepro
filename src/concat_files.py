#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar  4 16:52:33 2020

@author: antonio
"""
import os
import warnings
from utils.utils import warning_on_one_line
from shutil import copyfileobj, copyfile

warnings.formatwarning = warning_on_one_line


def concat_files(in_path, out_path = '.', is_concat=False):
    '''
    DESCRIPTION: concatenates plain text files into one with a \n separating 
    them.
    Input and output files must be UTF-8 encoded.
    In case we have already concatenated files as input, simply copy them.

    Parameters
    ----------
    in_path : string
        datapath to directory with all text files to be concatenated. UTF-8
        encoding!
    out_path : string
        datapath to file with concatenated files. UTF-8 conding!

    Returns
    -------
    None.

    '''
    
    # If files are already concatenated, just copy them
    if is_concat==False:
        for root, dirs, files in os.walk(in_path):
            for filename in files:
                copyfile(os.path.join(root, filename), os.path.join(out_path, filename))
        return
        
    
    listOfFiles = os.listdir(in_path)
    listOfFiles = list(map(lambda x: os.path.join(in_path, x), listOfFiles))
    with open(out_path,'w', encoding='utf8') as fout:
        for f in listOfFiles:
            with open(f,'r', encoding='utf8') as fin:
                copyfileobj(fin, fout)
            fout.write('\n')
    warnings.warn('Files order is arbitrary within a datapath')