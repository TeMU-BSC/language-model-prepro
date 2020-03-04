#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar  4 16:52:33 2020

@author: antonio
"""
import os
import warnings
from utils.utils import warning_on_one_line
from shutil import copyfileobj

warnings.formatwarning = warning_on_one_line


def concat_files(input_datapath, output_filepath = '.'):
    '''
    DESCRIPTION: concatenates plain text files into one with a \n separating 
    them.
    Input and output files must be UTF-8 encoded.

    Parameters
    ----------
    input_datapath : string
        datapath to directory with all text files to be concatenated. UTF-8
        encoding!
    output_filepath : string
        datapath to file with concatenated files. UTF-8 conding!

    Returns
    -------
    None.

    '''
    
    listOfFiles = os.listdir(input_datapath)
    listOfFiles = list(map(lambda x: os.path.join(input_datapath, x), listOfFiles))
    with open(output_filepath,'w', encoding='utf8') as fout:
        for f in listOfFiles:
            with open(f,'r', encoding='utf8') as fin:
                copyfileobj(fin, fout)
            fout.write('\n')
    warnings.warn('Files order is arbitrary within a datapath')