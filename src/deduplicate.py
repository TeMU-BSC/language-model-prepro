#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar  4 16:53:53 2020

@author: antonio
"""
from utils.utils import warning_on_one_line
import warnings

warnings.formatwarning = warning_on_one_line


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
    
    # Use this tool (also used by OSCAR)
    # https://github.com/whitfin/runiq
    return 