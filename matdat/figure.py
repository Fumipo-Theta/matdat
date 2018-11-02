import pandas as pd
import re
from func_helper import pip, identity
from .save_plot import actionSavePNG
from .i_subplot import ISubplot
from matpos import Matpos, FigureSizing

import matplotlib.pyplot as plt


class Figure:
    """
    複数行・複数列のサブプロットからなる図を作成するためのクラス.
    プロットデータとプロット方法を定義したSubplotを登録し,
        最後にレイアウトを指定して図を生成する.

    Example
    -------
    figure = Figure()

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

    axes = figure.show(size=(4,3), column=2, margin=(1,1),
        padding={"left": 1, "bottom": 1})
    # Grid layout with 2 column. All size are 4 x 3,
    #   margin is 1 and 1 for both direction.
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
    #    2  : matplotlib.pyplot.axsubplot,
    #    3  : matplotlib.pyplot.axsubplot
    # }

    # You can customize detail of them.
    axes[2].set_ylabel("c", fontsize=16)

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

    figure = Figure()

    axes = figure.show(size=subplot_sizes, column=2, margin=(1,1), padding = {"left": 1, "right": 0.2})
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

    from matpos import Matpos

    mp = Matpos()

    a = mp.from_left_top(mp,size=(4,3))
    b = mp.add_right(a, size=(4,3), offset=(1,0))
    c = mp.add_bottom(a, size=(None,2), offset=(0,1))
    d = mp.add_bottom(c, size=(4,1), offset=(0,1))

    figure = Figure()
    axes = figure.show(mp, [a,b,c,d], padding=padding)
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

    def __init__(self, *arg, **kwargs):
        self.subplots = []
        self.length = 0
        self.axIdentifier = []

    def get_length(self):
        return self.length

    def add_subplot(self, subplot, identifier=None):
        """
        subplot: Subplot
            has methods:
               plot: ax -> ax
        """
        if not isinstance(subplot, ISubplot):
            raise TypeError("subplot must inherit ISubplot.")

        self.subplots.append(subplot)
        self.axIdentifier.append(
            identifier if identifier != None else self.length+1)
        self.length = self.length + 1
        return self

    def show(self, *arg, **kwargs):
        """
        Parameters
        ----------
        *arg
            Same size grid mode
                None
                  or
                figure_sizing: FigureSizing

            Different size grid mode
                None

            Custom layout mode
                matpos: MatPos
                subgrids: Subgrids

        **kwargs
            size: tuple[float] | list[tuple[float]]
            column: int
            margin: tuple[float]
            padding: dict
            test: bool
            **compatible to matplotlib.figure.Figure

        Return
        ------
        axs: dict[str:matplotlib.axes._subplots.Axsubplot]


        """
        if len(arg) > 0:
            if type(arg[0]) is Matpos:
                matpos = arg[0]
                subgrids = arg[1]
                return self.__show_custom(matpos, subgrids, **kwargs)
            elif type(arg[0]) is FigureSizing:
                figure_sizing = arg[0]
                return self.__show_grid(
                    [figure_sizing.get_figsize()
                     for i in range(self.get_length())],
                    margin=figure_sizing.get_margin(),
                    padding=figure_sizing.get_padding(),
                    **kwargs
                )
            elif type(arg[0]) is dict:
                return self.show(**arg[0], **kwargs)
            else:
                raise SystemError(
                    "Type of positional arguments must be Matpos or dict. Or use keyword arguments.")

        else:
            if type(kwargs.get("size")) is tuple:
                size = kwargs.pop("size")

                return self.__show_grid(
                    [size for i in range(self.get_length())],
                    **kwargs
                )
            elif type(kwargs.get("size")) is list:
                sizes = kwargs.pop("size")

                return self.__show_grid(sizes, **kwargs)
            else:
                raise TypeError(
                    "The first arguments must be MatPos, Tuple, or List")

    def __show_grid(self, sizes, column=1, margin=(1, 0.5), padding={}, test=False, **kwargs):
        matpos = Matpos()
        sgs = matpos.add_grid(sizes, column, margin)

        return self.__show_custom(matpos, sgs, padding, test, **kwargs)

    def __show_custom(self, matpos, subgrids, padding={}, test=False, **kwargs):
        fig, empty_axes = Figure.generate_figure_and_axes(
            matpos, subgrids, padding, **kwargs)
        axes = Figure.plot_on_axes(empty_axes, self.subplots, test)
        return (fig, dict(zip(self.axIdentifier, axes)))

    @staticmethod
    def generate_figure_and_axes(matpos, subgrids, padding, **kwargs):
        return matpos.figure_and_axes(
            subgrids, padding=padding, **kwargs
        )

    @staticmethod
    def plot_on_axes(axes, subplots, test):
        return pip(
            Figure.__applyForEach(test),
            list
        )(zip(axes, subplots))

    @staticmethod
    def __applyForEach(test=False):
        """
        [(pyplot.axsubplot, Subplot)] -> [pyplot.axsubplot]
        """
        def helper(t):
            ax = t[0]
            subplot = t[1]
            return subplot.plot(ax, test)

        def f(axesAndSubplots):
            return map(
                helper,
                axesAndSubplots
            )
        return f

    def showIdentifier(self):
        print("Identifier of axes are: ")
        print(self.axIdentifier)

    def save(self, directory, fileName, ext="png"):
        saver = Figure.__IFigureSaver(ext)
        return saver(directory, fileName)()

    @staticmethod
    def __IFigureSaver(ext):
        if re.match(r"[pP](ng|NG)$", ext):
            print("save as png")
            return actionSavePNG
