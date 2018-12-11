import re
from func_helper import pip, identity
from .save_plot import actionSavePNG
from .i_subplot import ISubplot
from matpos import Matpos, FigureSizing


class Figure:
    """
    The class for managing multiple subplots.
    The instance register some instance of ISubplot.
    When generating image, you can indicate layout of the subplots.

    Parameters
    ----------
    None

    Methods
    -------
    add_subplot(subplot:ISubplot)
    show(*arg,**kwargs)

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

    # The unit of length can be also "mm", "cm", or "px".
    # The dpi parameter can be used.

    # If you want to plot by size of 300 x 200 px and dpi is 72:

    axes = figure.show(size=(300,200), column=2, margin=(50,50), padding = {"left": 50, "right": 10}, unit="px", dpi=72)

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
        self.axIdentifier = []

    def get_length(self):
        return len(self.subplots)

    def add_subplot(self, *subplot, name=[]):
        """
        subplot: Subplot
            has methods:
               plot: ax -> ax
        """
        if any(map(lambda s: not isinstance(s, ISubplot), subplot)):
            raise TypeError("subplot must inherit ISubplot.")

        for i, s in enumerate(subplot):
            self.subplots.append(s)
            self.axIdentifier.append(
                name[i]
                if type(name) is list and len(name) >= self.get_length()
                else name+str(self.get_length())
                if type(name) is str
                else self.get_length()
            )
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
                matpos: Matpos
                subgrids: Subgrids

        **kwargs
            size: tuple[float] | list[tuple[float]]
            column: int
            margin: tuple[float]
            padding: dict
            test: bool
            unit: str: "inches", "cm", "mm", or "px"
            dpi: int
            ** and other parameters compatible to matplotlib.figure.Figure

        Return
        ------
        fig: matplotlib.figure.Figure
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

    def __show_grid(self, sizes, column=1, margin=(1, 0.5), padding={}, test=False, unit="inches", dpi=72, **kwargs):
        matpos = Matpos(unit=unit, dpi=dpi)
        sgs = matpos.add_grid(sizes, column, margin)

        return self.__show_custom(matpos, sgs, padding, test, dpi=dpi, **kwargs)

    def __show_custom(self, matpos, subgrids, padding={}, test=False, **kwargs):
        fig, empty_axes = matpos.figure_and_axes(
            subgrids, padding=padding, **kwargs
        )

        axes = pip(
            Figure.__applyForEach(test),
            list
        )(zip(empty_axes, self.subplots))

        return (fig, dict(zip(self.axIdentifier, axes)))

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

    def save(self, directory, fileName, ext="png"):
        saver = Figure.__IFigureSaver(ext)
        return saver(directory, fileName)()

    @staticmethod
    def __IFigureSaver(ext):
        if re.match(r"[pP](ng|NG)$", ext):
            print("save as png")
            return actionSavePNG
