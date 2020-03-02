#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 10 10:57:35 2020

@author: antonio
"""
import argparse
from utils.utils import (to_plain_text, split_to_sentences,
                         handwritten_filters, concat_files, deduplicate)
from utils.general_utils import copy_dir_structure
import warnings
import os
from shutil import copyfile

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
    
    args = parser.parse_args()
    in_path = args.in_path
    out_path = args.out_path
    
    return in_path, out_path

    
if __name__ == '__main__':
    in_path, out_path = parse_args()
    
    in_path = '/home/antonio/Documents/Projects/BERT/prepro/data/toy_data/wiki'
    data_type = 'txt'
    target_lang = 'es'

    ## 0. ALL files to plain text, UTF-8 encoding
    if in_path[-1] == '/':
        out_path_txt = in_path[0:-1] + '_txt' + '/'
    else:
        out_path_txt = in_path + '_txt'
        
    copy_dir_structure(in_path, out_path_txt)
    to_plain_text(in_path, out_path_txt, data_type=data_type)
    
    #############  #############
    in_path_filters = out_path_txt
    if in_path_filters[-1] == '/':
        out_path_filters = in_path[0:-1] + '_filtered' + '/'
    else:
        out_path_filters = in_path + '_filtered'
        
    copy_dir_structure(in_path_filters, out_path_filters)
    for root, dirs, files in os.walk(in_path_filters):
        for filename in files:
            # Ignore empty files
            if os.path.getsize(os.path.join(root, filename)) == 0:
                continue
            
            # Read file
            with open(os.path.join(root, filename),'r', encoding='utf8') as f:
                text = f.read()
            
            ## TODO 1. Only natural language:
                # Removed header and tag material from newswire documents 
                    #-> do we have that? In crawler or what?
                    #-> that would be removed as too short sentences, right????
            
            ## TODO: 2. Machine translated and generated texts were removed using a simple 
            # support vector machine(SVM): remove documents
            
            ## 3. Split to sentences
            text_splitted = split_to_sentences(text)
            
            ## TODO: 4. Filter out DOCUMENTS: Language detection and noise: 
                # high a ratio  
            		# of digits,  
            		# uppercase,
            		# non-Spanish alphabetic characters -> needed? TODO
            	# low average sentence length
            to_keep = handwritten_filters(text_splitted, text, thres_length=100,
                                          thres_digit=0.9, thres_alpha=0.9, 
                                          thres_upper=0.9, thres_bad_sentences=0.9,
                                          target_lang='es',thres_conf=0.5)
            print(to_keep)
            ## TODO: 5. Further remove noise: ML to remove morphosyntactically similar 
                # sentences to 4: remove sentences
            
            
            ## 6. Save file
            if to_keep:
                output_filepath = os.path.join(root.replace(in_path_filters, 
                                                            out_path_filters),
                                               filename)
                copyfile(os.path.join(root, filename), output_filepath)

            
    ############ Concat all files and remove duplicated sentences ############
    ## 8. Concatenate files
    input_path_concat = out_path_filters + '/'
    concat_files(input_path_concat, out_path)
    
    ## TODO: 9. Deduplication: remove duplicated sentences??
    deduplicate(out_path)