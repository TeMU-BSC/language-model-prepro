#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 10 10:57:35 2020

@author: antonio
"""

from utils.utils import parse_args, warning_on_one_line, copy_dir_structure
import warnings
from normalize_files import normalize_files
from filter_files import filter_files
from concat_files import concat_files
from deduplicate import deduplicate
from time import time


warnings.formatwarning = warning_on_one_line



if __name__ == '__main__':
    in_path, out_path, is_concat = parse_args()
    
    '''in_path = '/home/antonio/Documents/Projects/BERT/prepro/data/toy_data/wiki'
    data_type = 'txt'
    target_lang = 'es'
    '''

    ### Replicate directory structure
    copy_dir_structure('../data/', '../output/')
    
    if is_concat == True:
        # TODO: need to write this
        pass
    else:
        ############# 0. ALL files to plain text, UTF-8 encoding #############
        print('\n\nTransforming files to plain UTF8 text...\n\n')
        out_path_txt = normalize_files(in_path)

        ############# 1. FILTERING #############
        print('\n\nFiltering out unsuitable documents...\n\n')
        in_path_filters = out_path_txt
        out_path_filters = filter_files(in_path_filters)
        
                
        ############ Concat all files and remove duplicated sentences ############
        print('\n\nConcatenating all files...\n\n')
        input_path_concat = out_path_filters + '/'
        concat_files(input_path_concat, out_path)
        
        ## TODO: Remove duplicated sentences ############
        print('\n\nRemoving duplicated sentences...\n\n')
        deduplicate(out_path)