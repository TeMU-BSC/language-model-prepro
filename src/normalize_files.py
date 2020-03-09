#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar  4 16:44:15 2020

@author: antonio
"""
import os
#import textract
import json
import csv
import warnings
import subprocess
import re
from utils.utils import (write_binary_sentence_splitted, rreplace,
                         flatten_json_iterative_solution, warning_on_one_line)

warnings.formatwarning = warning_on_one_line


def normalize_files(in_path, is_concat=False):
    '''
    Copy all files into a new directory with same folder structure and files
    transformed to plain text and UTF8 encoding. 
    Also, remove blank lines
    
    Parameters
    ----------
    in_path : str
        input path. Need to be in data folder
        
    Returns
    -------
    out_path : str
        output path.

    '''
    ### Define output path
    out_path = rreplace(in_path, '/data/', '/output/', 1)

    if out_path[-1] == '/':
        out_path = out_path[0:-1] + '_txt' + '/'
    else:
        out_path = out_path + '_txt'
    
    # Create _txt directory
    if not os.path.exists(out_path):
        os.makedirs(out_path)
        
    ### Normalize files
    to_plain_text(in_path, out_path, is_concat)
    
    return out_path

def to_plain_text(input_dirpath, output_dirpath, data_type='', is_concat=False):
    '''
    DESCRIPTION: receives datapath with non-plain text files and transforms them
    to plain text (very naïve, any lines with headers, ids, etc will be removed
    latter in the pipeline). Encodes them as UTF-8.

    Parameters
    ----------
    input_filepath : string
        filepath to input file.
    data_type: string
        Values: 'json', 'pdf', 'html', 'xml', 'csv', 'tsv', 'txt', 'other'
    output_filepath: string
        filepath to output file
        
        
    Returns
    -------
    None
    '''
    # TODO: Restructure this function in a prettier way
    
    for root, dirs, files in os.walk(input_dirpath):
        for filename in files:

            # Infer datatype from file extension  
            if data_type == '':
                data_type = filename.split('.')[-1]
                
            if data_type in ['pdf', 'html', 'xml', 'other']:
                #text = textract.process(filename, encoding='utf8')
                if data_type == 'pdf':
                    # TODO: fix some of wrong end of lines in pdfminer
                    # Replace \n by blankspace when followed by lowercase
                    #text = re.sub(b'\n+[a-z]', ' [a-z]', text) -> NOT WORKING (obviously)
                    warnings.warn('We are ignoring not json, tsv, csv or txt files')
                    pass
                # TODO: output to txt folder with UTF-8 encoding
                # write_binary_sentence_splitted(output_dirpath, filename, text)'''
        
            elif data_type == 'json':
                # Extract info
                with open(filename, 'r') as f:
                    js = json.load(f)
                text = list(flatten_json_iterative_solution(js).values())
                
                # Write
                write_binary_sentence_splitted(root, input_dirpath, 
                                               output_dirpath, filename, text)
                
            elif data_type == 'tsv':
                # Extract info
                text = []
                with open(filename, "r") as f:
                    reader = csv.reader(f, delimiter="\t")
                    for i, line in enumerate(reader):
                        for entry in line:
                            text.append(entry)
                            
                # Write
                write_binary_sentence_splitted(root, input_dirpath, 
                                               output_dirpath, filename, text)
                            
            elif data_type == 'csv':
                # Extract info
                text = []
                with open(filename, "r") as f:
                    reader = csv.reader(f, delimiter=",")
                    for i, line in enumerate(reader):
                        for entry in line:
                            text.append(entry)
                # Write
                write_binary_sentence_splitted(root, input_dirpath, 
                                               output_dirpath, filename, text)
        
            elif data_type == 'txt': # Convert to UTF-8 (call to system)
                output_filepath = os.path.join(root.replace(input_dirpath, 
                                                            output_dirpath),
                                               filename)
                # To UTF8
                with open(output_filepath, "w", encoding='utf8') as outfile:
                    subprocess.call(["iconv", "-t utf-8", 
                                     os.path.join(root,filename)], stdout=outfile)
                # Remove blank lines
                if is_concat == False:
                    with open(os.path.join(output_filepath), 'r', encoding='utf8') as f:
                        text = f.read()
                    text = text.strip('\n')
                    text = re.sub('\n+', '\n', text)    
                    with open(os.path.join(output_filepath), 'w', encoding='utf8') as f:
                        f.write(text)
