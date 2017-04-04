"""
    config_dir
    ----------
    Just stores a variable with the name of the current directory, that 
    is the base directory of the entire filesystem. 
"""
import os

base_dir = os.path.abspath(os.path.dirname(__file__))