#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 18 17:31:59 2020

@author: antonio
"""
import os

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