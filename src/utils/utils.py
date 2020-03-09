#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 10 11:43:20 2020

@author: antonio
"""

from sentence_splitter import SentenceSplitter # recommended by jordi
import os
from itertools import chain, starmap
import argparse

   
def split_to_sentences(text, target_lang='es'):
    '''
    DESCRIPTION: Split text into sentences.

    Parameters
    ----------
    text : string
        String with entire document.

    Returns
    -------
    sentences: list of str
        List with sentences of document

    '''  
    splitter = SentenceSplitter(language=target_lang)
    return splitter.split(text) 



def flatten_json_iterative_solution(dictionary):
    """Flatten a nested json file
    From: https://towardsdatascience.com/how-to-flatten-deeply-nested-json-objects-in-non-recursive-elegant-python-55f96533103d"""

    # Unpack one level only!!!
    def unpack(parent_key, parent_value):
        """Unpack one level of nesting in json file"""
        if isinstance(parent_value, dict):
            for key, value in parent_value.items():
                temp1 = parent_key + '_' + key
                yield temp1, value
        elif isinstance(parent_value, list):
            i = 0 
            for value in parent_value:
                temp2 = parent_key + '_'+str(i) 
                i += 1
                yield temp2, value
        else:
            yield parent_key, parent_value    


    # Keep iterating until the termination condition is satisfied
    while True:
        # Keep unpacking the json file until all values are atomic elements (not dictionary or list)
        dictionary = dict(chain.from_iterable(starmap(unpack, dictionary.items())))
        # Terminate condition: not any value in the json file is dictionary or list
        if not any(isinstance(value, dict) for value in dictionary.values()) and \
           not any(isinstance(value, list) for value in dictionary.values()):
               break
        
    return dictionary

def write_binary_sentence_splitted(root, input_dirpath, output_dirpath, 
                                   filename, text):
    '''
    DESCRIPTION: Eliminate blanklines and write list of sentences to binary 
    file in UTF-8 encoding.

    Parameters
    ----------
    output_filepath: string
        filepath to output file
    text: list of strings
        
        
    Returns
    -------
    None
    '''
    # Create output_filepath according to input and output directory paths and
    # Filename
    output_filepath = os.path.join(root.replace(input_dirpath, output_dirpath),
                                   filename)
    
    # Do not copy empty lines
    text.remove('\n')

    # Write file
    with open(output_filepath, 'wb') as f:
        for line in text:
            f.write(line.encode('utf8'))
            f.write(b'\n')
            

def copy_dir_structure(datapath, output_path_new_files):
    '''
    DESCRIPTION: copy folders structure in a new route.
            
    Parameters
    ----------
    datapath: str.
        Directory whose structure I want to replicate
    output_path_new_files: str. 
        Root directory on which I want to re-create the sub-folder structure.
    '''
    for dirpath, dirnames, filenames in os.walk(datapath):
        structure = os.path.join(output_path_new_files, 
                                 dirpath[len(datapath):])
        if not os.path.isdir(structure):
            os.mkdir(structure)
        else:
            print(structure)
            print("Folder does already exist!")
            
            
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
    parser.add_argument("-c", "--is_concat", required = False, default = False,
                        dest = "is_concat", 
                        help = "is the dataset concatenated in one file?")    
    args = parser.parse_args()

    return args.in_path, args.out_path, args.is_concat


def warning_on_one_line(message, category, filename, lineno, file=None, line=None):
    return '%s:%s: %s: %s\n' % (filename, lineno, category.__name__, message)

def rreplace(s, old, new, occurrence):
    '''
    Replace last occurrences of substring in string.
    From https://stackoverflow.com/questions/2556108/rreplace-how-to-replace-the-last-occurrence-of-an-expression-in-a-string

    Parameters
    ----------
    s : str
        string where I work on.
    old : str
        occurrence I want to remove.
    new : str
        occurrence I want to insert.
    occurrence : int
        Number of occurrences I want to substitute.

    Returns
    -------
    str
        new string.

    '''
    li = s.rsplit(old, occurrence)
    return new.join(li)