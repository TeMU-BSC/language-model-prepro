#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar  4 16:46:13 2020

@author: antonio
"""
import os
import numpy as np # needed?
from shutil import copyfile
import warnings
from langid.langid import LanguageIdentifier, model # fast
from utils.utils import copy_dir_structure, split_to_sentences, warning_on_one_line

warnings.formatwarning = warning_on_one_line


def filter_files(in_path, is_concat=False):
    '''
    Copy files that are suitable to a new directory. 
    In case we have already concatenated files as input (like the one 
    downloaded from OSCAR https://traces1.inria.fr/oscar/es/), keep only the 
    suitable lines from each file.
    
    Parameters
    ----------
    in_path : str
        input path.
        
    Returns
    -------
    out_path : str
        output path.

    '''
    
    ### Define output path
    if in_path[-1] == '/':
        out_path = in_path[0:-1] + '_filtered' + '/'
    else:
        out_path = in_path + '_filtered'
        
    ### Replicate directory structure
    copy_dir_structure(in_path, out_path)
    
    ### Copy suitable files
    for root, dirs, files in os.walk(in_path):
        for filename in files:

            # Decide whether it is suitable or not
            to_keep, concat_sentences = is_suitable(root, filename, is_concat)
            
            # Save file
            if is_concat == True:
                # Copy only selected lines
                output_filepath = os.path.join(root.replace(in_path, out_path),
                                               filename)
                with open(output_filepath, 'w', encoding = 'utf8') as f:
                    for concat_sentence in concat_sentences:
                        f.write(concat_sentence)
                continue
            
            if not to_keep:
                continue # Do not save unsuitable files
            
            output_filepath = os.path.join(root.replace(in_path, out_path),
                                           filename)
            copyfile(os.path.join(root, filename), output_filepath)
            
    if is_concat == True:
        warnings.warn('langid module is not very reliable at the sentence level, '+
                      'then, I am ignoring language detection')

    return out_path


def is_suitable(root, filename, is_concat):
    '''
    Decide whether a file is suitable, or not. 
    In case we have an already concatenated file as input (like the one 
    downloaded from OSCAR https://traces1.inria.fr/oscar/es/), decide which 
    lines to keep.

    Parameters
    ----------
    root : str
        path to parent filename folder.
    filename : str
        filename.
    is_concat: bool
        whether the input file is a concatenated one or not.

    Returns
    -------
    to_keep: bool
        Whether the file is suitable to be used in the NLP task or not.
    list
        List with the sentences to keep. Only non-empty when the input is an 
        already concatenated file.
        

    '''   

    # Ignore empty files
    if os.path.getsize(os.path.join(root, filename)) == 0:
        return False
    
    
    ###### A. If we have a concatenated file, get lines to keep ######
    if is_concat == True:       
        # Read file
        with open(os.path.join(root, filename),'r', encoding='utf8') as f:
            text_splitted = f.readlines()
            
        # Filter out unsuitable lines
        text_splitted_ok = heur_filters_concat(text_splitted, thres_length=10, 
                                               thres_digit=0.5, thres_alpha=0.3,
                                               thres_upper=0.5, target_lang='es',
                                               thres_conf=0.65)
        return True, text_splitted_ok
    
    ###### B. Otherwise, decide whether to keep file, or not ######
    # Read file
    with open(os.path.join(root, filename),'r', encoding='utf8') as f:
        text = f.read()
        
    ## TODO 1. Only natural language: removed header and tag material from 
    # newswire documents 
        # NOT NECESSARY FOR OUR OPUS CORPUS
    
    ## TODO: 2. Machine translated and generated texts were removed using a simple 
    # support vector machine(SVM): remove documents
        # NOT NECESSARY FOR OUR OPUS CORPUS
    
    ## 3. Split to sentences
    text_splitted = split_to_sentences(text)
    
    ## TODO: 4. Filter out DOCUMENTS: Language detection and noise: 
        # high a ratio  
    		# of digits,  
    		# uppercase,
    		# non-Spanish alphabetic characters -> needed? TODO
    	# low average sentence length
    to_keep = heur_filters(text_splitted, text, thres_length=100,
                                  thres_digit=0.9, thres_alpha=0.9, 
                                  thres_upper=0.9, thres_bad_sentences=0.9,
                                  target_lang='es',thres_conf=0.5)
    ## TODO: 5. Further remove noise: ML to remove morphosyntactically similar 
        # sentences to 4: remove sentences
    return to_keep,[]

def heur_filters(text_splitted, text, thres_length=10, thres_digit=0.5,
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
    bool
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
    if ((identifier.classify(text)[0] == target_lang) & 
        (identifier.classify(text)[1]>thres_conf)):
        return True
    else:
        return False
    
    
def heur_filters_concat(text_splitted, thres_length=10, thres_digit=0.5,
                    thres_alpha=0.3, thres_upper=0.5,  target_lang='es',
                    thres_conf=0.65):
    '''
    Remove lines: non-Spanish
              high a ratio: 
                        digits,  
                        uppercase,
              low average sentence length

    Parameters
    ----------
    text_splitted : list of strings
        List of lines in text.
    thres_length : int, optional
        Minimum sentence length to keep it.
    thres_digit : int, optional
        Maximum proportion of digits in sentence to keep it
    thres_alpha : float, optional
        Maximum proportion of non alphanumeric characters in sentence to keep it
    thres_upper : float, optional
        Maximum proportion of uppercase in sentence to keep it
    target_lang : str, optional
        Language code we want to keep (es, cat, eu, etc).
    thres_conf : float, optional
        Minimum language confidence to keep it
        

    Returns
    -------
    text_splitted : list of strings
        List of lines kept.

    '''
         
    to_remove = []

    for sentence, pos in zip(text_splitted, range(len(text_splitted))):
        # Ad-hoc filters
        l = len(sentence)
        perc_digits = sum(c.isdigit() for c in sentence) / l
        perc_upper = sum(c.isupper() for c in sentence) / l
        if ((l < thres_length) | (perc_digits > thres_digit) | 
            (perc_upper > thres_upper)):
            # TODO: set proper thresholds
            to_remove.append(pos)
            continue

        # Detect language (not very reliable at sentence level)
        '''identifier = LanguageIdentifier.from_modelstring(model, norm_probs=True)
        if ((identifier.classify(sentence)[0] != target_lang) | 
            ((identifier.classify(sentence)[0] == target_lang) & 
             (identifier.classify(sentence)[1]<thres_conf))):
            to_remove.append(pos)'''

    # Remove non-suitable sentences
    for index in sorted(set(to_remove), reverse=True):
        del text_splitted[index]

    return text_splitted