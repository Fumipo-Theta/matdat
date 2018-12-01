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
from .axes_style import *
from .scatter import scatter
from .line import line
from .vhlines import vlines
from .band import xband, yband
from .velocity import velocity
from .box import box, factor_box
from .violin import factor_violin
from .text import text
from .hist import hist
from .bar import bar, factor_bar
from .cycler import *
