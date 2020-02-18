#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 10 10:57:35 2020

@author: antonio
"""
import argparse
from utils.utils import (to_plain_text, split_to_sentences,
                         handwritten_filters, concat_files)
from utils.general_utils import copy_dir_structure
import warnings
import os

def warning_on_one_line(message, category, filename, lineno, file=None, line=None):
    return '%s:%s: %s: %s\n' % (filename, lineno, category.__name__, message)
warnings.formatwarning = warning_on_one_line


def parse_args():
    '''
    DESCRIPTION: parse arguments

    Returns
    -------
    in_path : str
        path to input files.
    out_path : str
        path to output file.

    '''
    parser = argparse.ArgumentParser(description='process user given parameters')
    parser.add_argument("-i", "--in_path", required = True, dest = "in_path", 
                        help = "path to input files")
    parser.add_argument("-o", "--out_path", required = True, dest = "out_path",
                        help = "path to output file")
    parser.add_argument("-d", "--data_type", required = True, dest = "data_type",
                        help = "path to output file")
    
    args = parser.parse_args()
    in_path = args.in_path
    out_path = args.out_path
    data_type = args.data_type
    
    return in_path, out_path, data_type

    
if __name__ == '__main__':
    in_path, out_path, data_type = parse_args()
    
    in_path = '/home/antonio/Documents/Projects/BERT/prepro/data/toy_data/wiki'
    data_type = 'txt'
    target_lang = 'es'

    ## 0. ALL files to plain text, UTF-8 encoding (INPUT: filepath, OUTPUT: filepath)
    if in_path[-1] == '/':
        out_path_txt = in_path[0:-1] + '_txt' + '/'
    else:
        out_path_txt = in_path + '_txt'
    copy_dir_structure(in_path, out_path_txt)
    to_plain_text(in_path, out_path_txt, data_type=data_type)
    
    ############# From now on, do this file by file #############
    # TODO: Remove empty files
    for root, dirs, files in os.walk(out_path_txt):
        for filename in files:
            
            # Read file
            with open(os.path.join(root, filename),'r', encoding='utf8') as f:
                text = f.read()
            ## 1. Split to sentences
            # TODO: properly integrate in pipeline
            text_splitted = split_to_sentences(text)
            
            ## 2. Removed header and tag material from newswire documents 
                    #-> do we have that? In crawler or what?
                    #-> that would be removed as too short sentences, right????
            
            ## 3. Machine translated and generated texts were removed using a simple 
            # support vector machine(SVM): remove documents
            
            ## 4. Filter out sentences: Language detection and remove noisy sentences: 
                # high a ratio  
            		# of digits,  
            		# uppercase,
            		# non-Spanish alphabetic characters -> needed?
            	# low average sentence length
            text_filtered = handwritten_filters(text_splitted, target_lang, 
                                                0.5, 10, 0.5, 0.9)
            
            ## 6. Further remove noise: ML to remove morphosyntactically similar 
                # sentences to 5: remove sentences
            
            
            ## 7. Save file
            
    ############ Concat all files and remove duplicated sentences ############
    ## 8. Concatenate files
    concat_files(input_datapath_x, out_path)
    
    ## 9. Deduplication: remove duplicated sentences??
