#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 10 11:43:20 2020

@author: antonio
"""

from sentence_splitter import SentenceSplitter # recommended by jordi
from langid.langid import LanguageIdentifier, model # fast
import numpy as np  # needed ?
import shutil
import os
import subprocess
from itertools import chain, starmap
import json
import csv
import textract
import warnings
from time import time


def to_plain_text(input_dirpath, output_dirpath, data_type=''):
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
    
    for root, dirs, files in os.walk(input_dirpath):
        for filename in files:

            # Infer datatype from file extension  
            if data_type == '':
                data_type = filename.split('.')[-1]
                
            if data_type in ['pdf', 'html', 'xml', 'other']:
                text = textract.process(filename, encoding='utf8')
                if data_type == 'pdf':
                    # TODO: fix some of wrong end of lines in pdfminer
                    # Replace \n by blankspace when followed by lowercase
                    #text = re.sub(b'\n+[a-z]', ' [a-z]', text) -> NOT WORKING (obviously)
                    pass
                # TODO: output to NON-Sentence-splitted folder with UTF-8 encoding
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
                with open(output_filepath, "w", encoding='utf8') as outfile:
                    subprocess.call(["iconv", "-t utf-8", 
                                     os.path.join(root,filename)], stdout=outfile)
   
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
                shutil.copyfileobj(fin, fout)
            fout.write('\n')
    warnings.warn('Files order is arbitrary within a datapath')
    
def handwritten_filters(text_splitted, text, thres_length=10, thres_digit=0.5,
                        thres_alpha=0.3, thres_upper=0.5, thres_bad_sentences=0.3,
                        target_lang='es',thres_conf=0.95):
    '''
    Remove documents: non-Spanish
                      high a ratio: 
                                digits,  
                                uppercase,
                      low average sentence length

    Parameters
    ----------
    text : list of strings
        Every element in the text is a string containing one single sentence.
    target_lang: str
        Language code we want to keep (es, cat, eu, etc)
    thres_length: int
        Minimum sentence length to keep it.
    thres_digit: float
        Maximum proportion of digits in sentence to keep it
    thres_upper: float
        Maximum proportion of uppercase in sentence to keep it
    thres_conf: float
        Minimum language confidence to keep it

    Returns
    -------
    _: bool
        Whether to keep document or not

    '''
         
    ## Length condition
    #text_len = list(map(lambda x: len(x) > thres_length, text_splitted))
    if (np.mean(list(map(lambda x: len(x), text_splitted))) < thres_length):
        return False
    
    ## Bad lines condition
    # Emtpy lines filter
    text_not_empty = list(filter(lambda x: len(x) > 0, text_splitted))
    # Digit ratio filter
    text_not_digit = list(filter(lambda x: (sum(c.isdigit() for c in x) / len(x)) < thres_digit,
                             text_not_empty))
    # Not alphanumeric filter
    text_not_alpha = list(filter(lambda x: (sum(c.isalnum() for c in x) / len(x)) < thres_alpha,
                             text_not_digit))
    # Uppercase ratio filter
    text_not_upper = list(filter(lambda x: (sum(c.isupper() for c in x) / len(x)) < thres_upper,
                             text_not_alpha))
    
    num_bad_sentences = len(text_splitted) - len(text_not_upper)
    
    if (num_bad_sentences/len(text_splitted)) > thres_bad_sentences:
        return False
        
    ## Language condition
    # TODO: check how this library works and whether it is good enough
    identifier = LanguageIdentifier.from_modelstring(model, norm_probs=True)
    if ((identifier.classify(text)[0] == target_lang) & (identifier.classify(text)[1]>thres_conf)):
        return True
    else:
        return False


def deduplicate(in_path):
    # TODO: write this
    '''
    Remove duplicated sentences in file. 
    Does it in clusters to speed up the code.

    Parameters
    ----------
    in_path : str
        Path to file I want to deduplicate.

    Returns
    -------
    None

    '''
    return 

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
    DESCRIPTION: Write list of sentences to binary file in UTF-8 encoding.

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
    # Write file
    with open(output_filepath, 'wb') as f:
        for line in text:
            f.write(line.encode('utf8'))
            f.write(b'\n')