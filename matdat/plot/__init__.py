"""
This module provides wrapper functions for plot with matplotlib.

By using with other modules in "matdat" and "matpos", you can separate actions of plot
    from data and layouting.

Functions
---------
set_tick_params
set_labels
set_grid
set_xlim
set_ylim
line
scatter
vlines
hlines
box
factor_box
factor_violin
velocity
band
text
"""

from .action import *
