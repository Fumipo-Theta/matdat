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

    axes = figure.show()
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
    subgrids = [
        (4,3),
        (4,3),
        (4,1),
        (4,1)
    ]

    # set padding around plot area when generate instance of Figure
    figure = Figure(padding={"left": 1, "right": 0.2})

    axes = figure.show_grid(subgrids, column=2, offset=(1,1))
    # Grid layout with 2 column.
    #
    # aaaa bbbb
    # aaaa bbbb
    # aaaa bbbb
    #
    # cccc dddd
    # cccc dddd
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

    from src.matpos import MatPos

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

    def __init__(self, figureStyle={}, padding=None):
        self.subplots = []
        self.figureStyle = {
            "titleSize": 16,
            "width": 8,
            "height": 6,
            "column": 1,
            "left": 0.1,
            "bottom": 0.1,
            "right": 0.99,
            "top": 0.95,
            "wspace": 0.2,
            "hspace": 0.2,
            **figureStyle
        }
        self.length = 0
        self.axIdentifier = []
        self.matpos = MatPos(padding)

    def get_length(self):
        return self.length

    def add_subplot(self, subplot, identifier=None):
        self.subplots.append(subplot)
        self.axIdentifier.append(
            identifier if identifier != None else self.length)
        self.length = self.length + 1

    def show(self, style={}, test=False):
        """

        """

        figureStyle = {**self.figureStyle, **style}

        fig = Figure._generateFigure(self.length, figureStyle)

        axes = pip(
            Figure._generateAxes(fig),
            Figure._applyForEach(test),
            list
        )(self.subplots)

        return dict(zip(self.axIdentifier, axes))

    def show_grid(self, sizes=[], column=1, distance=(1, 0.5), style={}, test=False):

        sgs = self.matpos.add_grid(sizes, column, distance)
        return self.show_custom(sgs, style, test)

    def show_custom(self, subgrids, style={}, test=False):
        fig, empty_axes = self.matpos.figure_and_axes(subgrids)

        axes = pip(
            Figure._applyForEach(test),
            list
        )(zip(empty_axes, self.subplots))

        return dict(zip(self.axIdentifier, axes))

    @staticmethod
    def _getGrid(col, totalNum):
        return {
            "row": int(totalNum/col)+(1 if totalNum % col != 0 else 0),
            "column": col
        }

    @staticmethod
    def _generateFigure(axNum, style):
        fst = dotdict(style)

        grid = Figure._getGrid(fst.column, axNum)

        fig = plt.figure(figsize=(
            fst.width * grid["column"],
            fst.height * grid["row"]
        ))
        fig.subplots_adjust(
            left=fst.left, bottom=fst.bottom,
            right=fst.right, top=fst.top,
            wspace=fst.wspace, hspace=fst.hspace
        )
        fig.patch.set_facecolor('white')
        if (fst.get("title") != None):
            plt.title(fst.title, fontsize=fst.titleSize)
        return (fig, grid)

    @staticmethod
    def _generateAxes(figAndGrid):
        """
        (pyplot.Figure, (int, int) -> {int,int})
            -> [Subplot]
            -> [(pyplot.saxsubplot, Subplot)]
        """
        fig, grid = figAndGrid

        def f(subplots):
            return pip(
                enumerate,
                mapping(lambda t: [
                    fig.add_subplot(
                        grid["row"], grid["column"], t[0]+1
                    ),
                    t[1]
                ]),
                list
            )(subplots)

        return f

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
