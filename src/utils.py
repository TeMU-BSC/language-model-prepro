#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 10 11:43:20 2020

@author: antonio
"""

from sentence_splitter import SentenceSplitter # recommended by jordi
from langid.langid import LanguageIdentifier, model # fast
import shutil
import os
import warnings
import subprocess
from itertools import chain, starmap
import json
import csv
import textract

def warning_on_one_line(message, category, filename, lineno, file=None, line=None):
    return '%s:%s: %s: %s\n' % (filename, lineno, category.__name__, message)
warnings.formatwarning = warning_on_one_line

target_lang = 'es'
identifier = LanguageIdentifier.from_modelstring(model, norm_probs=True)
splitter = SentenceSplitter(language=target_lang)

def to_plain_text(input_filepath, output_filepath, data_type='json'):
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
    
    # TODO: Infer datatype from file extension    
    # TODO: input_filepath is filepath or folder path?, output_filepath is filepath or folder_path?
    
    if data_type in ['pdf', 'html', 'xml', 'other']:
        text = textract.process(input_filepath, encoding='utf8')
        if data_type == 'pdf':
            # TODO: fix some of wrong end of lines in pdfminer
            # Replace \n by blankspace when followed by lowercase
            #text = re.sub(b'\n+[a-z]', ' [a-z]', text) -> NOT WORKING (obviously)
            pass
        # TODO: output to NON-Sentence-splitted folder with UTF-8 encoding
        # write_binary_sentence_splitted(output_filepath, text)'''

    elif data_type == 'json':
        # Extract info
        with open(input_filepath, 'r') as f:
            js = json.load(f)
        text = list(flatten_json_iterative_solution(js).values())
        output_filepath = ('.'.join(output_filepath.split('.')[0:-1]) + 
                           'sentence-splitted.' + output_filepath.split('.')[-1])
        # Write
        write_binary_sentence_splitted(output_filepath, text)
        
    elif data_type == 'tsv':
        # Extract info
        text = []
        with open(input_filepath, "r") as f:
            reader = csv.reader(f, delimiter="\t")
            for i, line in enumerate(reader):
                for entry in line:
                    text.append(entry)
        # Write
        write_binary_sentence_splitted(output_filepath, text)
                    
    elif data_type == 'csv':
        # Extract info
        text = []
        with open(input_filepath, "r") as f:
            reader = csv.reader(f, delimiter=",")
            for i, line in enumerate(reader):
                for entry in line:
                    text.append(entry)
        # Write
        write_binary_sentence_splitted(output_filepath, text)

    elif data_type == 'txt': # Convert to UTF-8 (call to system)
        with open(output_filepath, "w", encoding='utf8') as outfile:
            subprocess.call(["iconv", "-t utf-8", input_filepath], stdout=outfile)
   
def split_to_sentences(text):
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
    listOfFiles = list(map(lambda x: input_datapath + x, listOfFiles))
    with open(output_filepath,'w', encoding='utf8') as fout:
        for f in listOfFiles:
            with open(f,'r', encoding='utf8') as fin:
                shutil.copyfileobj(fin, fout)
            fout.write('\n')
    warnings.warn('Files order is arbitrary within a datapath')
    
def handwritten_filters(text, target_lang, thres_digit=0.5, thres_length=10, 
                        thres_upper=0.5, thres_conf=0.9):
    '''
    Remove sentences: non-Spanish
                    high a ratio: 
                        its,  
                        uppercase,
                        non-spanish alphabetic characters -> necessary??
                    low average sentence length

    Parameters
    ----------
    text : list of strings
        Every element in the text is a string containing one single sentence.
    target_lang: str
        Language code we want to keep (es, cat, eu, etc)

    Returns
    -------
    text: list
        List with sentences we will keep

    '''
    
    to_remove = []
    
    for sentence, pos in zip(text, range(len(text))):
        # Ad-hoc filters
        l = len(sentence)
        perc_digits = sum(c.isdigit() for c in sentence) / l
        perc_upper = sum(c.isupper() for c in sentence) / l
        if ((l < thres_length) | (perc_digits > thres_digit) | 
            (perc_upper > thres_upper)):
            # TODO: set proper thresholds
            to_remove.append(pos)
            continue
        
        # Detect language
        lang, conf = identifier.classify(sentence)
        if (lang != target_lang) | ((lang == target_lang) & (conf < thres_conf)):
            to_remove.append(pos)
            
    # Remove non-suitable sentences
    for index in sorted(set(to_remove), reverse=True):
        del text[index]
        
    return text

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

def write_binary_sentence_splitted(output_filepath, text):
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
    output_filepath = ('.'.join(output_filepath.split('.')[0:-1]) + 
       'sentence-splitted.' + output_filepath.split('.')[-1])
    with open(output_filepath, 'wb') as f:
        for line in text:
            f.write(line.encode('utf8'))
            f.write(b'\n')