#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 10 10:57:35 2020

@author: antonio
"""
import argparse
from utils import *

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
    
    return in_path, out_path

    
if __name__ == '__main__':
    in_path, out_path, data_type = parse_args()
    target_lang = 'es'
    # TODO: For file in directory! Need to iterate within directory

    ## 0. Discard empty files

    ## 0. Files to plain text, UTF-8 encoding
    to_plain_text(in_path, out_path, data_type=data_type)
    
    ## 1. Split to sentences
    # TODO: properly integrate in pipeline
    text_splitted = split_to_sentences(text)
    
    ## 2. Removed header and tag material from newswire documents 
            #-> do we have that? In crawler or what'?
            #-> that would be removed as too short sentences, right????
    
    ## 3. Machine translated and generated texts were removed using a simple 
    # support vector machine(SVM): remove documents
    
    ## 4. Filter out sentences: Language detection and remove noisy sentences: 
        # high a ratio  
    		# of digits,  
    		# uppercase,
    		# non-Spanish alphabetic characters -> needed?
    	# low average sentence length
    text_splitted = handwritten_filters(text_splitted, target_lang, 0.5, 10, 0.5, 0.9)
    
    ## 6. Further remove noise: ML to remove morphosyntactically similar 
        # sentences to 5: remove sentences
    
    
    ## 7. Deduplication: remove texts or sentences??
    
    ## 8. Concatenate files
    concat_files(input_datapath, output_filepath)
