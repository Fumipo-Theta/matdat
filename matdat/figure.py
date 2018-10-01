import pandas as pd
from func_helper import pip, tee, mapping, filtering, reducing, identity
from .csv_reader import CsvReader
from .dotdict import dotdict
from .get_path import PathList, getFileList
from .save_plot import actionSavePNG
from matpos import MatPos

from IPython.display import display
import matplotlib.pyplot as plt


class Figure:
    """
    複数行・複数列のサブプロットからなる図を作成するためのクラス.
    プロットデータとプロット方法を定義したSubplotを登録し,
        最後にレイアウトを指定して図を生成する.

    Example
    -------
    # overwrite each subplot size as 10 (inch), column of subplots as 2
    figure = Figure({"width" : 10, "column": 2})

    # add 4 subplots
    figure.add_subplot(subplot1, "a")
    figure.add_subplot(subplot2, "b")
    figure.add_subplot(subplot3)
    figure.add_subplot(subplot4)

    # ============================================================
    # Simple grid layout mode
    #
    # Grid layout with subplots having the same size.
    # Distance between subplots are defined by instance variables
    # =============================================================

    axes = figure.show((4,3), 2, (1,1))
    # Grid layout with 2 column. All size are 4 x 3, margin is 1 and 1
    #   for both direction.
    #
    # aaaa bbbb
    # aaaa bbbb
    # aaaa bbbb
    #
    # cccc dddd
    # cccc dddd
    # cccc dddd
    #
    # Added subplots are returned as dictionary.
    # Each subplots can be identified by their name or order.
    # axes = {
    #   "a" : matplotlib.pyplot.axsubplot,
    #   "b" : matplotlib.pyplot.axsubplot,
    #    3  : matplotlib.pyplot.axsubplot,
    #    4  : matplotlib.pyplot.axsubplot
    # }

    # You can customize detail of them.
    axes[3].set_ylabel("c", fontsize=16)

    # save image as png
    figure.save("./image/","image.png")

    # ========================
    # Complex grid layout mode
    #
    # Grid layput with subplots
    # having different size
    # ========================

    # List of the size of subplots (width, height)
    subplot_sizes = [
        (4,3),
        (4,3),
        (4,1),
        (4,1)
    ]

    # set padding around plot area when generate instance of Figure
    figure = Figure(padding={"left": 1, "right": 0.2})

    axes = figure.show_grid(subplot_sizes, column=2, margin=(1,1))
    # Grid layout with 2 column.
    #
    # aaaa bbbb
    # aaaa bbbb
    # aaaa bbbb
    #
    # cccc dddd
    #
    # The 1st row is 2 subplot having size of 4 x 3 (unit of inches)
    # The 2nd row is 2 subplot having size of 4 x 1.
    # Distance between plot areas of subplots is, 1 inch for horizontal
    #   direction and also 1 inch for vertical direction.

    # ========================================
    # Free layout mode with subgrids by MatPos
    #
    # Size and position of each subplot can be
    # customized.
    # ========================================

    from matpos import MatPos

    mp = MatPos()

    a = mp.from_left_top(mp,size=(4,3))
    b = mp.add_right(a, size=(4,3), offset=(1,0))
    c = mp.add_bottom(a, size=(None,2), offset=(0,1))
    d = mp.add_bottom(c, size=(4,1), offset=(0,1))

    figure = Figure(padding=padding)
    axes = figure.show_custom([a,b,c,d])
    # Subgrids are defined their size and relative position
    # from the other subgrid.
    # If element of size is None, it indicates expanding to
    #  fit the figure width or height at that time.
    #
    # aaaa bbbb
    # aaaa bbbb
    # aaaa bbbb
    #
    # ccccccccc
    # ccccccccc
    #
    # dddd
    """

    def __init__(self, figureStyle={}):
        self.subplots = []
        self.figureStyle = {
            "titleSize": 16,
            **figureStyle
        }
        self.length = 0
        self.axIdentifier = []

    def get_length(self):
        return self.length

    def add_subplot(self, subplot, identifier=None):
        self.subplots.append(subplot)
        self.axIdentifier.append(
            identifier if identifier != None else self.length)
        self.length = self.length + 1

    def show(self, size, column=1, margin=(1, 0.5), padding={}, test=False):
        """
        Grid layout by the same subplot size and margin.
        """

        return self.show_grid(
            [size for i in range(self.get_length())],
            column,
            margin,
            padding,
            test
        )

    def show_grid(self, sizes=[], column=1, margin=(1, 0.5), padding={}, test=False):
        matpos = MatPos()
        sgs = matpos.add_grid(sizes, column, margin)

        return self.show_custom(matpos, sgs, padding, test)

    def show_custom(self, matpos, subgrids, padding={}, test=False):
        fig, empty_axes = matpos.figure_and_axes(subgrids, padding=padding)

        axes = pip(
            Figure._applyForEach(test),
            list
        )(zip(empty_axes, self.subplots))

        return dict(zip(self.axIdentifier, axes))

    @staticmethod
    def _applyForEach(test=False):
        """
        [(pyplot.axsubplot, Subplot)] -> [pyplot.axsubplot]
        """
        def helper(t):
            return t[1].plot(t[0], test)

        def f(axesAndSubplots):
            return map(
                helper,
                axesAndSubplots
            )
        return f

    def showIdentifier(self):
        print("Identifier of axes are: ")
        display(self.axIdentifier)

    def save(self, directory, fileName):
        return actionSavePNG(directory, fileName)
